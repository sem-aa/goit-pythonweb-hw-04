import asyncio
import argparse
import logging

from aiopath import AsyncPath
from aioshutil import copyfile

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="copy files from source to output folder by extensions"
    )
    parser.add_argument("source", help="source folder")
    parser.add_argument("output", help="output folder")
    return parser.parse_args()


async def read_folder(path: AsyncPath, output: AsyncPath) -> None:
    try:
        tasks = []
        async for element in path.iterdir():
            if await element.is_dir():
                tasks.append(read_folder(element, output))
            else:
                tasks.append(copy_file(element, output))

        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error reading folder {path}: {e}")


async def copy_file(file: AsyncPath, output: AsyncPath) -> None:
    try:
        extension = file.suffix.lstrip(".").lower() or "other"
        target_dir = output / extension
        await target_dir.mkdir(parents=True, exist_ok=True)
        await copyfile(file, target_dir / file.name)
    except Exception as e:
        logging.error(f"Error copying file {file}: {e}")


if __name__ == "__main__":
    args = parse_args()
    source = AsyncPath(args.source)
    output = AsyncPath(args.output)
    asyncio.run(read_folder(source, output))
