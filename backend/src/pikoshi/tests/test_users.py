import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio(loop_scope="function")
async def test_my_crud_function(db_session: AsyncSession):
    pass
