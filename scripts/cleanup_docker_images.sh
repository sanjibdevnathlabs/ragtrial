#!/bin/bash
set -euo pipefail

# =============================================================================
# Docker Hub Image Cleanup Script
# =============================================================================
# Usage:
#   ./cleanup_docker_images.sh <repo-name> [mode] [branch-hash]
#
# Examples:
#   ./cleanup_docker_images.sh ragtrial-base              # Cleanup base images
#   ./cleanup_docker_images.sh ragtrial                   # Cleanup app images
#   ./cleanup_docker_images.sh ragtrial-base delete-branch br-abc123  # Delete all branch images
#
# Modes:
#   - (default): Normal cleanup (keep last 5 master, 3 per branch)
#   - delete-branch: Delete ALL images for a specific branch hash
#
# Environment:
#   DRY_RUN=1         - Don't actually delete, just show what would be deleted
#   DOCKERHUB_USERNAME - Docker Hub username
#   DOCKERHUB_TOKEN    - Docker Hub personal access token
# =============================================================================

NAMESPACE="sanjibdevnath"
REPO=${1:-}
MODE=${2:-cleanup}
BRANCH_HASH=${3:-}

KEEP_MASTER=5
KEEP_BRANCH=3

# Dry-run mode (set DRY_RUN=1 to test without deleting)
DRY_RUN=${DRY_RUN:-0}

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate inputs
if [ -z "$REPO" ]; then
  echo -e "${RED}Error: Repository name required${NC}"
  echo "Usage: $0 <repo-name> [mode] [branch-hash]"
  exit 1
fi

# Load credentials from environment/dockerenv.toml if running locally
if [ -f "environment/dockerenv.toml" ] && [ -z "${DOCKERHUB_USERNAME:-}" ]; then
  echo -e "${BLUE}📁 Loading credentials from environment/dockerenv.toml${NC}"
  export DOCKERHUB_USERNAME=$(grep USERNAME environment/dockerenv.toml | cut -d'=' -f2 | tr -d ' ')
  export DOCKERHUB_TOKEN=$(grep PASSWORD environment/dockerenv.toml | cut -d'=' -f2 | tr -d ' ')
  export DRY_RUN=1
  echo -e "${YELLOW}⚠️  DRY_RUN mode enabled (local testing)${NC}"
fi

if [ -z "${DOCKERHUB_USERNAME:-}" ] || [ -z "${DOCKERHUB_TOKEN:-}" ]; then
  echo -e "${RED}Error: DOCKERHUB_USERNAME and DOCKERHUB_TOKEN required${NC}"
  exit 1
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Docker Hub Image Cleanup${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Repository: ${GREEN}$NAMESPACE/$REPO${NC}"
echo -e "Mode: ${GREEN}$MODE${NC}"
if [ "$DRY_RUN" = "1" ]; then
  echo -e "Dry Run: ${YELLOW}ENABLED (no actual deletions)${NC}"
else
  echo -e "Dry Run: ${RED}DISABLED (will delete images!)${NC}"
fi
echo -e "${BLUE}============================================${NC}"
echo ""

# Authenticate
echo -e "${BLUE}🔐 Authenticating with Docker Hub...${NC}"
TOKEN=$(curl -s -H "Content-Type: application/json" -X POST \
  -d "{\"username\": \"$DOCKERHUB_USERNAME\", \"password\": \"$DOCKERHUB_TOKEN\"}" \
  https://hub.docker.com/v2/users/login/ | jq -r .token)

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Authentication failed${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Authenticated successfully${NC}"
echo ""

# Fetch ALL tags (handle pagination)
fetch_all_tags() {
  local url="https://hub.docker.com/v2/repositories/$NAMESPACE/$REPO/tags/?page_size=100"
  local all_tags=""
  
  echo -e "${BLUE}📥 Fetching all tags...${NC}"
  
  while [ -n "$url" ]; do
    response=$(curl -s -H "Authorization: JWT $TOKEN" "$url")
    tags=$(echo "$response" | jq -r '.results[] | "\(.name)|\(.last_updated)|\(.images // [] | length)"')
    
    if [ -n "$tags" ]; then
      all_tags="$all_tags$tags"$'\n'
    fi
    
    url=$(echo "$response" | jq -r '.next // empty')
  done
  
  echo "$all_tags"
}

# Get detailed tag information (with manifests)
get_tag_details() {
  local tag=$1
  echo -e "${BLUE}  🔍 Fetching manifest details for: $tag${NC}"
  
  response=$(curl -s -H "Authorization: JWT $TOKEN" \
    "https://hub.docker.com/v2/repositories/$NAMESPACE/$REPO/tags/$tag/")
  
  # Extract manifest information
  local manifest_count=$(echo "$response" | jq -r '.images | length')
  local manifests=$(echo "$response" | jq -r '.images[] | "      - \(.architecture) / \(.os): \(.digest[0:19])..."')
  
  echo -e "${YELLOW}    📦 $manifest_count manifest(s):${NC}"
  if [ -n "$manifests" ]; then
    echo "$manifests"
  fi
}

# Delete tag
delete_tag() {
  local tag=$1
  local show_details=${2:-false}
  
  if [ "$show_details" = "true" ]; then
    get_tag_details "$tag"
  fi
  
  if [ "$DRY_RUN" = "1" ]; then
    echo -e "${YELLOW}  [DRY-RUN] Would delete tag: $tag${NC}"
    if [ "$show_details" = "true" ]; then
      echo -e "${YELLOW}  ⚠️  This will also delete all associated manifests shown above${NC}"
    fi
  else
    echo -e "${RED}🗑️  Deleting tag: $tag${NC}"
    curl -s -X DELETE -H "Authorization: JWT $TOKEN" \
      "https://hub.docker.com/v2/repositories/$NAMESPACE/$REPO/tags/$tag/" > /dev/null
    echo -e "${GREEN}✅ Deleted tag and all associated manifests${NC}"
  fi
  echo ""
}

# Delete all tags matching a specific branch hash
delete_branch_images() {
  local branch_hash=$1
  echo -e "${BLUE}🗑️  Deleting ALL images for branch: $branch_hash${NC}"
  echo ""
  
  ALL_TAGS=$(fetch_all_tags)
  BRANCH_TAG_INFO=$(echo "$ALL_TAGS" | grep "^${branch_hash}|" || true)
  
  if [ -z "$BRANCH_TAG_INFO" ]; then
    echo -e "${YELLOW}ℹ️  No images found for branch: $branch_hash${NC}"
    return
  fi
  
  local count=0
  local total_manifests=0
  while IFS='|' read -r tag date manifest_count; do
    [ -z "$tag" ] && continue
    count=$((count + 1))
    total_manifests=$((total_manifests + manifest_count))
    echo -e "${BLUE}Tag $count: $tag (${manifest_count} manifest(s))${NC}"
    delete_tag "$tag" true
  done <<< "$BRANCH_TAG_INFO"
  
  echo ""
  echo -e "${GREEN}✅ Deleted $count tag(s) with $total_manifests total manifest(s) for branch: $branch_hash${NC}"
}

# Main cleanup logic
cleanup_images() {
  echo -e "${BLUE}📦 Analyzing $REPO images...${NC}"
  echo ""
  
  ALL_TAGS=$(fetch_all_tags)
  
  if [ -z "$ALL_TAGS" ]; then
    echo -e "${YELLOW}ℹ️  No tags found${NC}"
    return
  fi
  
  # Separate tags by type
  MASTER_TAGS=$(echo "$ALL_TAGS" | grep -E '^[0-9a-f]{40}\|' | sort -t'|' -k2 -r || true)
  BRANCH_TAGS=$(echo "$ALL_TAGS" | grep -E '^br-' | sort -t'|' -k2 -r || true)
  LATEST_TAG=$(echo "$ALL_TAGS" | grep -E '^latest\|' || true)
  
  # Count tags
  MASTER_COUNT=$(echo "$MASTER_TAGS" | grep -c '^' || echo 0)
  BRANCH_COUNT=$(echo "$BRANCH_TAGS" | grep -c '^' || echo 0)
  
  # Calculate total manifests
  TOTAL_MANIFESTS=0
  while IFS='|' read -r tag date manifest_count; do
    [ -z "$tag" ] && continue
    TOTAL_MANIFESTS=$((TOTAL_MANIFESTS + manifest_count))
  done <<< "$ALL_TAGS"
  
  echo -e "${BLUE}📊 Tag Summary:${NC}"
  echo -e "  Master tags (SHA): $MASTER_COUNT"
  echo -e "  Branch tags (br-*): $BRANCH_COUNT"
  echo -e "  Latest tag: $([ -n "$LATEST_TAG" ] && echo 'Yes' || echo 'No')"
  echo -e "  ${YELLOW}Total manifests across all tags: $TOTAL_MANIFESTS${NC}"
  echo -e "  ${YELLOW}(Each tag can have multiple manifests for different platforms)${NC}"
  echo ""
  
  # 1. Cleanup master tags (keep last 5)
  if [ "$MASTER_COUNT" -gt 0 ]; then
    echo -e "${BLUE}🔍 Processing master tags (keep last $KEEP_MASTER)...${NC}"
    echo ""
    local count=0
    local deleted=0
    while IFS='|' read -r tag date manifest_count; do
      [ -z "$tag" ] && continue
      count=$((count + 1))
      if [ $count -gt $KEEP_MASTER ]; then
        echo -e "${BLUE}Tag #$count: $tag (${manifest_count} manifest(s))${NC}"
        delete_tag "$tag" true
        deleted=$((deleted + 1))
      fi
    done <<< "$MASTER_TAGS"
    
    if [ $deleted -eq 0 ]; then
      echo -e "${GREEN}✅ All master tags within retention limit${NC}"
    else
      echo -e "${GREEN}✅ Processed $deleted master tag(s)${NC}"
    fi
    echo ""
  fi
  
  # 2. Cleanup branch tags (keep last 3 per branch hash)
  if [ "$BRANCH_COUNT" -gt 0 ]; then
    echo -e "${BLUE}🔍 Processing branch tags (keep last $KEEP_BRANCH)...${NC}"
    echo ""
    
    # Get unique branch hashes (works with bash 3.x)
    UNIQUE_HASHES=$(echo "$BRANCH_TAGS" | cut -d'|' -f1 | \
      grep -oE 'br-[a-f0-9]+' | sort -u || true)
    
    local total_deleted=0
    while read -r base_hash; do
      [ -z "$base_hash" ] && continue
      
      echo -e "${BLUE}  Processing group: $base_hash${NC}"
      
      # Get all tags for this branch hash
      GROUP_TAGS=$(echo "$BRANCH_TAGS" | grep "^${base_hash}" | \
        sort -t'|' -k2 -r || true)
      
      local group_count=0
      local group_deleted=0
      while IFS='|' read -r tag date manifest_count; do
        [ -z "$tag" ] && continue
        group_count=$((group_count + 1))
        if [ $group_count -gt $KEEP_BRANCH ]; then
          echo -e "  ${BLUE}Tag #$group_count: $tag (${manifest_count} manifest(s))${NC}"
          delete_tag "$tag" true
          group_deleted=$((group_deleted + 1))
          total_deleted=$((total_deleted + 1))
        fi
      done <<< "$GROUP_TAGS"
      
      if [ $group_deleted -eq 0 ]; then
        echo -e "  ${GREEN}✅ All tags within retention limit${NC}"
      else
        echo -e "  ${GREEN}✅ Processed $group_deleted tag(s)${NC}"
      fi
      echo ""
    done <<< "$UNIQUE_HASHES"
    
    echo -e "${GREEN}✅ Total branch tags processed: $total_deleted${NC}"
    echo ""
  fi
}

# Execute based on mode
case "$MODE" in
  delete-branch)
    if [ -z "$BRANCH_HASH" ]; then
      echo -e "${RED}Error: Branch hash required for delete-branch mode${NC}"
      exit 1
    fi
    delete_branch_images "$BRANCH_HASH"
    ;;
  
  cleanup)
    cleanup_images
    ;;
  
  *)
    echo -e "${RED}Error: Invalid mode: $MODE${NC}"
    echo "Valid modes: cleanup, delete-branch"
    exit 1
    ;;
esac

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo -e "${BLUE}============================================${NC}"

