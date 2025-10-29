"""
API models package.

Models are co-located with their respective modules:
- app/modules/upload/request.py + response.py
- app/modules/files/request.py + response.py
- app/modules/query/request.py + response.py
- app/modules/health/request.py + response.py
- app/api/models/common.py (shared models like ErrorResponse)

Import models directly from their modules:
    from app.modules.upload.response import UploadResponse
    from app.modules.query.request import QueryRequest
    from app.api.models.common import ErrorResponse
"""
