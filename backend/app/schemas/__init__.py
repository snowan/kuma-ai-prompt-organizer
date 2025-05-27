# Make schemas a proper package
from .auth import (
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserLogin,
    UserInDB,
    UserResponse,
    LikeBase,
    LikeCreate,
    LikeResponse
)

from .prompt import (
    PromptBase,
    PromptCreate,
    PromptUpdate,
    PromptInDBBase,
    Prompt,
    PromptWithLikes,
    PromptResponse
)

from .category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryInDBBase,
    Category,
    CategoryResponse
)

from .tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagInDBBase,
    Tag,
    TagResponse
)

__all__ = [
    'Token',
    'TokenData',
    'UserBase',
    'UserCreate',
    'UserLogin',
    'UserInDB',
    'UserResponse',
    'LikeBase',
    'LikeCreate',
    'LikeResponse',
    'PromptBase',
    'PromptCreate',
    'PromptUpdate',
    'PromptInDBBase',
    'Prompt',
    'PromptWithLikes',
    'PromptResponse',
    'CategoryBase',
    'CategoryCreate',
    'CategoryUpdate',
    'CategoryInDBBase',
    'Category',
    'CategoryResponse',
    'TagBase',
    'TagCreate',
    'TagUpdate',
    'TagInDBBase',
    'Tag',
    'TagResponse'
]
