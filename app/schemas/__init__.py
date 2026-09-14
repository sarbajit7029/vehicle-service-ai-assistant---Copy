from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

from app.schemas.booking import (
    BookingStatus,
    ServiceBookingCreate,
    ServiceBookingResponse,
    ServiceBookingUpdate,
)

from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageCreate,
    ChatSource,
    ChatResponse,
    ChatHistoryMessage,
    ChatHistoryResponse,
)

from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)

from app.schemas.document import (
    DocumentStatus,
    DocumentType,
    DocumentUploadRequest,
    KnowledgeChunkResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentUpdate,
)

from app.schemas.job_card import (
    JobCardCreate,
    JobCardResponse,
    JobCardStatus,
    JobCardUpdate,
)

from app.schemas.service_type import (
    ServiceTypeCreate,
    ServiceTypeResponse,
    ServiceTypeUpdate,
)

from app.schemas.technician import (
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
)

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserRole,
    UserUpdate,
)

from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)