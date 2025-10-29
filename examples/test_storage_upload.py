"""
Storage Upload Demo.

Demonstrates file upload to storage backends.
Tests both local and S3 storage with real operations.

Usage:
    # Test local storage
    python examples/test_storage_upload.py

    # Test S3 storage (requires ~/.aws config or AWS credentials)
    python examples/test_storage_upload.py --backend s3
"""

import argparse
from io import BytesIO
from pathlib import Path

from config import Config
from storage_backend import create_storage


def test_local_storage():
    """Test local storage backend."""
    print("\n" + "=" * 60)
    print("TESTING LOCAL STORAGE")
    print("=" * 60 + "\n")

    # Load config
    config = Config()
    config.storage.backend = "local"

    # Create storage
    storage = create_storage(config)
    print(f"✓ Created local storage: {storage.storage_path}")

    # Create test file
    test_filename = "test_upload.txt"
    test_content = b"This is a test file uploaded via local storage backend.\n"
    test_content += b"Upload time: " + str(Path(__file__).stat().st_mtime).encode()

    # Upload file
    print(f"\n→ Uploading {test_filename}...")
    result = storage.upload_file(BytesIO(test_content), test_filename)
    print(f"✓ Uploaded: {result}")

    # Verify file exists
    exists = storage.file_exists(test_filename)
    print(f"✓ File exists: {exists}")

    # Get metadata
    metadata = storage.get_file_metadata(test_filename)
    print(f"✓ File size: {metadata['size']} bytes")
    print(f"✓ Modified: {metadata['modified_time']}")

    # List files
    files = storage.list_files()
    print(f"✓ Total files in storage: {len(files)}")

    # Download file
    print(f"\n→ Downloading {test_filename}...")
    downloaded = storage.download_file(test_filename)
    downloaded_content = downloaded.read()
    print(f"✓ Downloaded {len(downloaded_content)} bytes")

    # Verify content
    if downloaded_content == test_content:
        print("✓ Content matches original!")
    else:
        print("✗ Content mismatch!")

    print("\n" + "=" * 60)
    print("LOCAL STORAGE TEST PASSED ✓")
    print("=" * 60 + "\n")


def test_s3_storage():
    """Test S3 storage backend."""
    print("\n" + "=" * 60)
    print("TESTING S3 STORAGE")
    print("=" * 60 + "\n")

    # Load config
    config = Config()
    config.storage.backend = "s3"

    print("→ Initializing S3 storage...")
    print(f"  Bucket: {config.storage.s3.bucket_name}")
    print(f"  Region: {config.storage.s3.region}")
    print(f"  Endpoint: {config.storage.s3.endpoint_url or 'AWS S3'}")
    print("\n→ Discovering AWS credentials...")
    print("  Checking:")
    print("    1. IAM Role (EC2/ECS/Lambda)")
    print("    2. IRSA (Kubernetes)")
    print("    3. Environment variables (AWS_ACCESS_KEY_ID)")
    print("    4. ~/.aws/credentials")
    print("    5. ~/.aws/config")

    try:
        # Create storage (this will discover credentials)
        storage = create_storage(config)
        print(f"\n✓ Connected to S3 bucket: {storage.bucket_name}")
        print(f"✓ Using region: {storage.region}")

        # Check credential source
        credentials = storage.session.get_credentials()
        if credentials:
            print(f"✓ Credentials found via: {credentials.method}")

        # Create test file
        test_filename = "test_s3_upload.txt"
        test_content = b"This is a test file uploaded to S3.\n"
        test_content += b"Uploaded via boto3 with automatic credential discovery.\n"

        # Upload file
        print(f"\n→ Uploading {test_filename} to S3...")
        result = storage.upload_file(BytesIO(test_content), test_filename)
        print(f"✓ Uploaded to S3: s3://{storage.bucket_name}/{result}")

        # Verify file exists
        exists = storage.file_exists(test_filename)
        print(f"✓ File exists in S3: {exists}")

        # Get metadata
        metadata = storage.get_file_metadata(test_filename)
        print(f"✓ File size: {metadata['size']} bytes")
        print(f"✓ Modified: {metadata['modified_time']}")
        print(f"✓ ETag: {metadata['etag']}")

        # List files
        files = storage.list_files()
        print(f"✓ Total files in S3 bucket: {len(files)}")

        # Download file
        print(f"\n→ Downloading {test_filename} from S3...")
        downloaded = storage.download_file(test_filename)
        downloaded_content = downloaded.read()
        print(f"✓ Downloaded {len(downloaded_content)} bytes from S3")

        # Verify content
        if downloaded_content == test_content:
            print("✓ Content matches original!")
        else:
            print("✗ Content mismatch!")

        print("\n" + "=" * 60)
        print("S3 STORAGE TEST PASSED ✓")
        print("=" * 60 + "\n")

        print("\n💡 CREDENTIAL DISCOVERY WORKED!")
        print(f"   boto3 automatically found credentials via: {credentials.method}")
        print("   Your ~/.aws configuration is working correctly! ✓")

    except Exception as e:
        print(f"\n✗ S3 Storage test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check ~/.aws/credentials file exists")
        print("  2. Check ~/.aws/config file exists")
        print("  3. Verify AWS credentials with: aws sts get-caller-identity")
        print("  4. Ensure S3 bucket exists: aws s3 ls")
        print("  5. Check bucket permissions")
        return False

    return True


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Test storage backends")
    parser.add_argument(
        "--backend",
        choices=["local", "s3", "both"],
        default="both",
        help="Storage backend to test",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("STORAGE BACKEND UPLOAD TEST")
    print("=" * 60)

    try:
        if args.backend in ["local", "both"]:
            test_local_storage()

        if args.backend in ["s3", "both"]:
            test_s3_storage()

        print("\n✅ ALL TESTS PASSED!\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
