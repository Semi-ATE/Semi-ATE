import asyncio
import async_timeout
from contextlib import asynccontextmanager
from typing import Optional, Tuple, Any
import pytest

# async_timeout.timeout with custom message (actually
# arbitrary args to BaseException constructor) and optional suppress
# https://github.com/aio-libs/async-timeout
@asynccontextmanager
async def timeout_ex(delay: Optional[float], *args: Tuple[Any, ...], suppress_exc: bool = False):
    t = None
    try:
        async with async_timeout.timeout(delay) as t:
            yield t
    except asyncio.TimeoutError as e:
        if t is not None and t.expired:
            if suppress_exc:
                return
            raise asyncio.TimeoutError(*args) from e
        raise


@pytest.mark.asyncio
async def test_async_timeout_with_custom_message():
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with timeout_ex(1, 'custom message'):
            await asyncio.sleep(2)
    assert 'custom message' in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_timeout_no_timeout():
    async with timeout_ex(2, 'custom message'):
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_async_timeout_original_message_on_nested():
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with timeout_ex(2, 'custom message'):
            await asyncio.sleep(1)
            raise asyncio.TimeoutError('exception raised by inner block')

    assert 'exception raised by inner block' in str(excinfo.value)
    assert 'custom message' not in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_timeout_custom_message_with_nested_from_inner():
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with timeout_ex(3, 'custom message outer'):
            await asyncio.sleep(1)
            async with timeout_ex(1, 'custom message inner'):
                await asyncio.sleep(2)

    assert 'custom message inner' in str(excinfo.value)
    assert 'custom message outer' not in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_timeout_custom_message_with_nested_from_outer():
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with timeout_ex(2, 'custom message outer'):
            await asyncio.sleep(1)
            async with timeout_ex(3, 'custom message inner'):
                await asyncio.sleep(2)

    assert 'custom message inner' not in str(excinfo.value)
    assert 'custom message outer' in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_timeout_with_suppress():
    async with timeout_ex(1, suppress_exc=True) as t:
        await asyncio.sleep(2)
    assert t.expired


@pytest.mark.asyncio
async def test_async_timeout_outer_suppress_with_inner_timeout():
    with pytest.raises(asyncio.TimeoutError) as excinfo:
        async with timeout_ex(3, suppress_exc=True):
            await asyncio.sleep(1)
            async with timeout_ex(1, 'custom message inner'):
                await asyncio.sleep(2)

    assert 'custom message inner' in str(excinfo.value)
