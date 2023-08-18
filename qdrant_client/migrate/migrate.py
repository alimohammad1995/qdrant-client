from enum import Enum
from typing import Dict, List, Optional

from qdrant_client import models
from qdrant_client._pydantic_compat import to_dict
from qdrant_client.client_base import QdrantBase


class MigrationCollisionAction(str, Enum):
    """Action on collection collision"""

    RAISE = "Raise"
    RECREATE = "Recreate"
    SKIP = "Skip"


def migrate(
    source_client: QdrantBase,
    dest_client: QdrantBase,
    collection_names: Optional[List[str]],
    on_collision_action: MigrationCollisionAction = MigrationCollisionAction.RAISE,
    batch_size: int = 100,
):
    """
    Migrate collections from source client to destination client

    Args:
        source_client (QdrantBase): Source client
        dest_client (QdrantBase): Destination client
        collection_names (list[str], optional): List of collection names to migrate.
            If None - migrate all source client collections. Defaults to None.
        on_collision_action (MigrationCollisionAction): Action on collection collision. Defaults to
            MigrationCollisionAction.RAISE.
        batch_size (int, optional): Batch size for scrolling and uploading vectors. Defaults to 100.
    """
    collection_names = select_source_collections(source_client, collection_names)
    collisions = find_collisions(dest_client, collection_names)
    absent_dest_collections = set(collection_names) - set(collisions)

    if collisions and on_collision_action == MigrationCollisionAction.RAISE:
        raise ValueError(f"Collections already exist in dest_client: {collisions}")
    elif collisions and on_collision_action == MigrationCollisionAction.SKIP:
        collisions = []

    for collection_name in absent_dest_collections:
        recreate_collection(source_client, dest_client, collection_name)
        migrate_collection(source_client, dest_client, collection_name, batch_size)

    for collection_name in collisions:
        recreate_collection(source_client, dest_client, collection_name)
        migrate_collection(source_client, dest_client, collection_name, batch_size)


def select_source_collections(source_client: QdrantBase, collection_names: List[str]) -> List[str]:
    source_collections = source_client.get_collections().collections
    source_collection_names = {collection.name for collection in source_collections}

    if collection_names:
        assert all(
            collection_name in source_collection_names for collection_name in collection_names
        ), f"Source client does not have collections: {set(collection_names) - source_collection_names}"
    else:
        collection_names = source_collection_names
    return collection_names


def find_collisions(dest_client: QdrantBase, collection_names: List[str]) -> List[str]:
    dest_collections = dest_client.get_collections().collections
    dest_collection_names = {collection.name for collection in dest_collections}
    existing_dest_collections = dest_collection_names & set(collection_names)
    return list(existing_dest_collections)


def recreate_collection(
    source_client: QdrantBase,
    dest_client: QdrantBase,
    collection_name: str,
) -> None:
    src_collection_info = source_client.get_collection(collection_name)
    src_config = src_collection_info.config
    src_payload_schema = src_collection_info.payload_schema

    dest_client.recreate_collection(
        collection_name,
        vectors_config=src_config.params.vectors,
        shard_number=src_config.params.shard_number,
        replication_factor=src_config.params.replication_factor,
        write_consistency_factor=src_config.params.write_consistency_factor,
        on_disk_payload=src_config.params.on_disk_payload,
        hnsw_config=models.HnswConfigDiff(**to_dict(src_config.hnsw_config)),
        optimizers_config=models.OptimizersConfigDiff(**to_dict(src_config.optimizer_config)),
        wal_config=models.WalConfigDiff(**to_dict(src_config.wal_config)),
        quantization_config=src_config.quantization_config,
    )

    recreate_payload_schema(dest_client, collection_name, src_payload_schema)


def recreate_payload_schema(
    dest_client: QdrantBase,
    collection_name: str,
    payload_schema: Dict[str, models.PayloadIndexInfo],
) -> None:
    for field_name, field_info in payload_schema.items():
        dest_client.create_payload_index(
            collection_name,
            field_name=field_name,
            field_schema=field_info.type if field_info.params is None else field_info.params,
        )


def migrate_collection(
    source_client: QdrantBase,
    dest_client: QdrantBase,
    collection_name: str,
    batch_size: int = 100,
) -> None:
    """Migrate collection from source client to destination client

    Args:
        collection_name (str): Collection name
        source_client (QdrantBase): Source client
        dest_client (QdrantBase): Destination client
        batch_size (int, optional): Batch size for scrolling and uploading vectors. Defaults to 100.
    """
    records, next_offset = source_client.scroll(
        collection_name, limit=batch_size, with_vectors=True
    )
    dest_client.upload_records(collection_name, records)
    while next_offset:
        records, next_offset = source_client.scroll(
            collection_name, offset=next_offset, limit=batch_size, with_vectors=True
        )
        dest_client.upload_records(collection_name, records)

    source_client_vectors_count = source_client.get_collection(collection_name).vectors_count
    dest_client_vectors_count = dest_client.get_collection(collection_name).vectors_count
    assert (
        source_client_vectors_count == dest_client_vectors_count
    ), f"Migration failed, vectors count are not equal: source vector count {source_client_vectors_count}, dest vector count {dest_client_vectors_count}"
