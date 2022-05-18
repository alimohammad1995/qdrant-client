from typing import Dict

from qdrant_client import grpc
from qdrant_client.http.models import models as http
from qdrant_client.uploader.grpc_uploader import json_to_value


class GrpcToRest:

    @classmethod
    def convert_condition(cls, model: grpc.Condition) -> http.Condition:
        if model.field:
            return cls.convert_field_condition(model.field)
        if model.filter:
            return cls.convert_filter(model.filter)
        if model.has_id:
            return cls.convert_has_id_condition(model.has_id)
        if model.is_empty:
            return cls.convert_is_empty_condition(model.is_empty)

    @classmethod
    def convert_filter(cls, model: grpc.Filter) -> http.Filter:
        return http.Filter(
            must=[cls.convert_condition(condition) for condition in model.must],
            should=[cls.convert_condition(condition) for condition in model.should],
            must_not=[cls.convert_condition(condition) for condition in model.must_not]
        )

    @classmethod
    def convert_range(cls, model: grpc.Range) -> http.Range:
        return http.Range(
            gt=model.gt,
            gte=model.gte,
            lt=model.lt,
            lte=model.lte,
        )

    @classmethod
    def convert_geo_radius(cls, model: grpc.GeoRadius) -> http.GeoRadius:
        return http.GeoRadius(
            center=cls.convert_geo_point(model.center),
            radius=model.radius
        )

    @classmethod
    def convert_collection_description(cls, model: grpc.CollectionDescription) -> http.CollectionDescription:
        return http.CollectionDescription(name=model.name)

    @classmethod
    def convert_collection_info(cls, model: grpc.CollectionInfo) -> http.CollectionInfo:
        return http.CollectionInfo(config=cls.convert_collection_config(model.config),
                                   disk_data_size=model.disk_data_size,
                                   optimizer_status=cls.convert_optimizer_status(model.optimizer_status),
                                   payload_schema=cls.convert_payload_schema(model.payload_schema),
                                   ram_data_size=model.ram_data_size,
                                   segments_count=model.segments_count,
                                   status=cls.convert_collection_status(model.status),
                                   vectors_count=model.vectors_count
                                   )

    @classmethod
    def convert_collection_config(cls, model: grpc.CollectionConfig) -> http.CollectionConfig:
        return http.CollectionConfig(
            hnsw_config=cls.convert_hnsw_config(model.hnsw_config),
            optimizer_config=cls.convert_optimizer_config(model.optimizer_config),
            params=cls.convert_collection_params(model.params),
            wal_config=cls.convert_wal_config(model.wal_config)
        )

    @classmethod
    def convert_hnsw_config(cls, model: grpc.HnswConfigDiff) -> http.HnswConfig:
        return http.HnswConfig(ef_construct=model.ef_construct, m=model.m,
                               full_scan_threshold=model.full_scan_threshold)

    @classmethod
    def convert_optimizer_config(cls, model: grpc.OptimizersConfigDiff) -> http.OptimizersConfig:
        return http.OptimizersConfig(
            default_segment_number=model.default_segment_number,
            deleted_threshold=model.deleted_threshold,
            flush_interval_sec=model.flush_interval_sec,
            indexing_threshold=model.indexing_threshold,
            max_optimization_threads=model.max_optimization_threads,
            max_segment_size=model.max_segment_size,
            memmap_threshold=model.memmap_threshold,
            payload_indexing_threshold=model.payload_indexing_threshold,
            vacuum_min_vector_number=model.vacuum_min_vector_number
        )

    @classmethod
    def convert_collection_params(cls, model: grpc.CollectionParams) -> http.CollectionParams:
        return http.CollectionParams(
            distance=cls.convert_distance(model.distance),
            shard_number=model.shard_number,
            vector_size=model.vector_sie
        )

    @classmethod
    def convert_distance(cls, model: grpc.Distance) -> http.Distance:
        if model == grpc.Distance.Cosine:
            return http.Distance.COSINE
        elif model == grpc.Distance.Euclid:
            return http.Distance.EUCLID
        elif model == grpc.Distance.Dot:
            return http.Distance.DOT
        else:
            raise NotImplementedError()

    @classmethod
    def convert_update_result(cls, model: grpc.UpdateResult) -> http.UpdateResult:
        return http.UpdateResult(operation_id=model.operation_id, status=cls.convert_update_status(model.status))

    @classmethod
    def convert_update_status(cls, model: grpc.UpdateStatus) -> http.UpdateStatus:
        if model == grpc.UpdateStatus.Acknowledged:
            return http.UpdateStatus.ACKNOWLEDGED
        elif model == grpc.UpdateStatus.Completed:
            return http.UpdateStatus.COMPLETED
        else:
            raise NotImplementedError()

    @classmethod
    def convert_has_id_condition(cls, model: grpc.HasIdCondition) -> http.HasIdCondition:
        return http.HasIdCondition(
            has_id=[cls.convert_point_id(idx) for idx in model.has_id]
        )

    @classmethod
    def convert_point_id(cls, model: grpc.PointId) -> http.ExtendedPointId:
        if model.num:
            return model.num
        if model.uuid:
            return model.uuid
        raise ValueError(f"invalid PointId model: {model}")

    @classmethod
    def convert_delete_alias(cls, model: grpc.DeleteAlias) -> http.DeleteAlias:
        raise NotImplementedError()

    @classmethod
    def convert_rename_alias(cls, model: grpc.RenameAlias) -> http.RenameAlias:
        raise NotImplementedError()

    @classmethod
    def convert_is_empty_condition(cls, model: grpc.IsEmptyCondition) -> http.IsEmptyCondition:
        return http.IsEmptyCondition(is_empty=http.PayloadField(key=model.key))

    @classmethod
    def convert_search_params(cls, model: grpc.SearchParams) -> http.SearchParams:
        raise NotImplementedError()

    @classmethod
    def convert_create_alias(cls, model: grpc.CreateAlias) -> http.CreateAlias:
        raise NotImplementedError()

    @classmethod
    def convert_create_collection(cls, model: grpc.CreateCollection) -> http.CreateCollection:
        raise NotImplementedError()

    @classmethod
    def convert_scored_point(cls, model: grpc.ScoredPoint) -> http.ScoredPoint:
        raise NotImplementedError()

    @classmethod
    def convert_values_count(cls, model: grpc.ValuesCount) -> http.ValuesCount:
        return http.ValuesCount(
            gt=model.gt,
            gte=model.gte,
            lt=model.lt,
            lte=model.lte,
        )

    @classmethod
    def convert_geo_bounding_box(cls, model: grpc.GeoBoundingBox) -> http.GeoBoundingBox:
        return http.GeoBoundingBox(
            bottom_right=cls.convert_geo_point(model.bottom_right),
            top_left=cls.convert_geo_point(model.top_left)
        )

    @classmethod
    def convert_point_struct(cls, model: grpc.PointStruct) -> http.PointStruct:
        raise NotImplementedError()

    @classmethod
    def convert_hnsw_config_diff(cls, model: grpc.HnswConfigDiff) -> http.HnswConfigDiff:
        raise NotImplementedError()

    @classmethod
    def convert_field_condition(cls, model: grpc.FieldCondition) -> http.FieldCondition:
        geo_bounding_box = cls.convert_geo_bounding_box(model.geo_bounding_box) if model.geo_bounding_box else None
        geo_radius = cls.convert_geo_radius(model.geo_radius) if model.geo_radius else None
        match = cls.convert_match(model.match) if model.match else None
        range_ = cls.convert_range(model.range) if model.range else None
        values_count = cls.convert_values_count(model.values_count) if model.values_count else None
        return http.FieldCondition(
            key=model.key,
            geo_bounding_box=geo_bounding_box,
            geo_radius=geo_radius,
            match=match,
            range=range_,
            values_count=values_count,
        )

    @classmethod
    def convert_match(cls, model: grpc.Match) -> http.Match:
        if model.integer:
            return http.MatchValue(value=model.integer)
        if model.boolean:
            return http.MatchValue(value=model.boolean)
        if model.keyword:
            return http.MatchValue(value=model.keyword)
        raise ValueError(f"invalid Match model: {model}")

    @classmethod
    def convert_wal_config_diff(cls, model: grpc.WalConfigDiff) -> http.WalConfigDiff:
        raise NotImplementedError()

    @classmethod
    def convert_collection_config(cls, model: grpc.CollectionConfig) -> http.CollectionConfig:
        raise NotImplementedError()

    @classmethod
    def convert_collection_params(cls, model: grpc.CollectionParams) -> http.CollectionParams:
        raise NotImplementedError()

    @classmethod
    def convert_optimizers_config_diff(cls, model: grpc.OptimizersConfigDiff) -> http.OptimizersConfigDiff:
        raise NotImplementedError()

    @classmethod
    def convert_update_collection(cls, model: grpc.UpdateCollection) -> http.UpdateCollection:
        raise NotImplementedError()

    @classmethod
    def convert_geo_point(cls, model: grpc.GeoPoint) -> http.GeoPoint:
        return http.GeoPoint(
            lat=model.lat,
            lon=model.lon,
        )

    @classmethod
    def convert_alias_operations(cls, model: grpc.AliasOperations) -> http.AliasOperations:
        raise NotImplementedError()

    @classmethod
    def convert_points_selector(cls, model: grpc.PointsSelector) -> http.PointsSelector:
        raise NotImplementedError()


class RestToGrpc:
    @classmethod
    def convert_filter(cls, model: http.Filter) -> grpc.Filter:
        return grpc.Filter(
            must=[cls.convert_condition(condition) for condition in model.must] if model.must is not None else None,
            must_not=[cls.convert_condition(condition) for condition in
                      model.must_not] if model.must_not is not None else None,
            should=[cls.convert_condition(condition) for condition in
                    model.should] if model.should is not None else None,
        )

    @classmethod
    def convert_range(cls, model: http.Range) -> grpc.Range:
        return grpc.Range(
            lt=model.lt,
            gt=model.gt,
            gte=model.gte,
            lte=model.lte,
        )

    @classmethod
    def convert_geo_radius(cls, model: http.GeoRadius) -> grpc.GeoRadius:
        return grpc.GeoRadius(
            center=cls.convert_geo_point(model.center),
            radius=model.radius
        )

    @classmethod
    def convert_collection_description(cls, model: http.CollectionDescription) -> grpc.CollectionDescription:
        return grpc.CollectionDescription(
            name=model.name
        )

    @classmethod
    def convert_collection_info(cls, model: http.CollectionInfo) -> grpc.CollectionInfo:
        return grpc.CollectionInfo(
            config=cls.convert_collection_config(model.config) if model.config else None,
            disk_data_size=model.disk_data_size,
            optimizer_status=cls.convert_optimizer_status(model.optimizer_status),
            payload_schema=cls.convert_payload_schema(
                model.payload_schema) if model.payload_schema is not None else None,
            ram_data_size=model.ram_data_size,
            segments_count=model.segments_count,
            status=cls.convert_collection_status(model.status),
            vectors_count=model.vectors_count,
        )

    @classmethod
    def convert_collection_status(cls, model: http.CollectionStatus) -> grpc.CollectionStatus:
        if model == http.CollectionStatus.RED:
            return grpc.CollectionStatus.Red
        if model == http.CollectionStatus.YELLOW:
            return grpc.CollectionStatus.Yellow
        if model == http.CollectionStatus.GREEN:
            return grpc.CollectionStatus.Green

        raise ValueError(f"invalid CollectionStatus model: {model}")

    @classmethod
    def convert_optimizer_status(cls, model: http.OptimizersStatus) -> grpc.OptimizerStatus:
        if isinstance(model, http.OptimizersStatusOneOf):
            return grpc.OptimizerStatus(
                ok=True,
            )
        if isinstance(model, http.OptimizersStatusOneOf1):
            return grpc.OptimizerStatus(
                ok=False,
                error=model.error
            )
        raise ValueError(f"invalid OptimizersStatus model: {model}")

    @classmethod
    def convert_payload_schema(cls, model: Dict[str, http.PayloadIndexInfo]) -> Dict[str, grpc.PayloadSchemaInfo]:
        return dict(
            (key, cls.convert_payload_index_info(val))
            for key, val in model.items()
        )

    @classmethod
    def convert_payload_index_info(cls, model: http.PayloadIndexInfo) -> grpc.PayloadSchemaInfo:
        return grpc.PayloadSchemaInfo(
            data_type=cls.convert_payload_schema_type(model.data_type)
        )

    @classmethod
    def convert_payload_schema_type(cls, model: http.PayloadSchemaType) -> grpc.PayloadSchemaType:
        if model == http.PayloadSchemaType.KEYWORD:
            return grpc.PayloadSchemaType.Keyword
        if model == http.PayloadSchemaType.INTEGER:
            return grpc.PayloadSchemaType.Integer
        if model == http.PayloadSchemaType.FLOAT:
            return grpc.PayloadSchemaType.Float
        if model == http.PayloadSchemaType.GEO:
            return grpc.PayloadSchemaType.Geo

        raise ValueError(f"invalid PayloadSchemaType model: {model}")

    @classmethod
    def convert_collection_status(cls, model: http.UpdateResult) -> grpc.UpdateResult:
        return grpc.UpdateResult(
            operation_id=model.operation_id,
            status=cls.convert_update_stats(model.status)
        )

    @classmethod
    def convert_update_result(cls, model: http.UpdateResult) -> grpc.UpdateResult:
        return grpc.UpdateResult(
            operation_id=model.operation_id,
            status=cls.convert_update_stats(model.status)
        )

    @classmethod
    def convert_update_stats(cls, model: http.UpdateStatus) -> grpc.UpdateStatus:
        if model == http.UpdateStatus.COMPLETED:
            return grpc.UpdateStatus.Completed
        if model == http.UpdateStatus.ACKNOWLEDGED:
            return grpc.UpdateStatus.Acknowledged

        raise ValueError(f"invalid UpdateStatus model: {model}")

    @classmethod
    def convert_has_id_condition(cls, model: http.HasIdCondition) -> grpc.HasIdCondition:
        return grpc.HasIdCondition(
            has_id=[cls.convert_extended_point_id(idx) for idx in model.has_id]
        )

    @classmethod
    def convert_delete_alias(cls, model: http.DeleteAlias) -> grpc.DeleteAlias:
        return grpc.DeleteAlias(
            alias_name=model.alias_name
        )

    @classmethod
    def convert_rename_alias(cls, model: http.RenameAlias) -> grpc.RenameAlias:
        return grpc.RenameAlias(
            old_alias_name=model.old_alias_name,
            new_alias_name=model.new_alias_name
        )

    @classmethod
    def convert_is_empty_condition(cls, model: http.IsEmptyCondition) -> grpc.IsEmptyCondition:
        return grpc.IsEmptyCondition(
            key=model.is_empty.key
        )

    @classmethod
    def convert_search_params(cls, model: http.SearchParams) -> grpc.SearchParams:
        return grpc.SearchParams(
            hnsw_ef=model.hnsw_ef
        )

    @classmethod
    def convert_create_alias(cls, model: http.CreateAlias) -> grpc.CreateAlias:
        return grpc.CreateAlias(
            collection_name=model.collection_name,
            alias_name=model.alias_name
        )

    @classmethod
    def convert_create_collection(cls, model: http.CreateCollection, collection_name: str) -> grpc.CreateCollection:
        return grpc.CreateCollection(
            collection_name=collection_name,
            distance=cls.convert_distance(model.distance) if model.distance else None,
            hnsw_config=cls.convert_hnsw_config_diff(model.hnsw_config) if model.hnsw_config else None,
            optimizers_config=cls.convert_optimizers_config_diff(
                model.optimizers_config) if model.optimizers_config else None,
            shard_number=model.shard_number,
            vector_size=model.vector_size,
            wal_config=cls.convert_wal_config_diff(model.wal_config) if model.wal_config else None,
        )

    @classmethod
    def convert_scored_point(cls, model: http.ScoredPoint) -> grpc.ScoredPoint:
        return grpc.ScoredPoint(
            id=cls.convert_extended_point_id(model.id),
            payload=cls.convert_payload(model.payload) if model.payload is not None else None,
            score=model.score,
            vector=model.vector,
            version=model.version
        )

    @classmethod
    def convert_values_count(cls, model: http.ValuesCount) -> grpc.ValuesCount:
        return grpc.ValuesCount(
            lt=model.lt,
            gt=model.gt,
            gte=model.gte,
            lte=model.lte,
        )

    @classmethod
    def convert_geo_bounding_box(cls, model: http.GeoBoundingBox) -> grpc.GeoBoundingBox:
        return grpc.GeoBoundingBox(
            top_left=cls.convert_geo_point(model.top_left),
            bottom_right=cls.convert_geo_point(model.bottom_right),
        )

    @classmethod
    def convert_point_struct(cls, model: http.PointStruct) -> grpc.PointStruct:
        return grpc.PointStruct(
            id=cls.convert_extended_point_id(model.id),
            vector=model.vector,
            payload=cls.convert_payload(model.payload) if model.payload is not None else None
        )

    @classmethod
    def convert_payload(cls, model: http.Payload) -> Dict[str, grpc.betterproto_lib_google_protobuf.Value]:
        return dict((key, json_to_value(val)) for key, val in model.items())

    @classmethod
    def convert_hnsw_config_diff(cls, model: http.HnswConfigDiff) -> grpc.HnswConfigDiff:
        return grpc.HnswConfigDiff(
            ef_construct=model.ef_construct,
            full_scan_threshold=model.full_scan_threshold,
            m=model.m,
        )

    @classmethod
    def convert_field_condition(cls, model: http.FieldCondition) -> grpc.FieldCondition:
        return grpc.FieldCondition(
            key=model.key,
            match=cls.convert_match(model.match) if model.match else None,
            range=cls.convert_range(model.range) if model.range else None,
            geo_bounding_box=cls.convert_geo_bounding_box(model.geo_bounding_box) if model.geo_bounding_box else None,
            geo_radius=cls.convert_geo_radius(model.geo_radius) if model.geo_radius else None,
            values_count=cls.convert_values_count(model.values_count) if model.values_count else None,
        )

    @classmethod
    def convert_wal_config_diff(cls, model: http.WalConfigDiff) -> grpc.WalConfigDiff:
        return grpc.WalConfigDiff(
            wal_capacity_mb=model.wal_capacity_mb,
            wal_segments_ahead=model.wal_segments_ahead
        )

    @classmethod
    def convert_collection_config(cls, model: http.CollectionConfig) -> grpc.CollectionConfig:
        return grpc.CollectionConfig(
            params=cls.convert_collection_params(model.params),
            hnsw_config=cls.convert_hnsw_config(model.hnsw_config),
            optimizer_config=cls.convert_optimizer_config(model.optimizer_config),
            wal_config=cls.convert_wal_config(model.wal_config)
        )

    @classmethod
    def convert_hnsw_config(cls, model: http.HnswConfig) -> grpc.HnswConfigDiff:
        return grpc.HnswConfigDiff(
            ef_construct=model.ef_construct,
            full_scan_threshold=model.full_scan_threshold,
            m=model.m,
        )

    @classmethod
    def convert_optimizer_config(cls, model: http.OptimizersConfig) -> grpc.OptimizersConfigDiff:
        return grpc.OptimizersConfigDiff(
            default_segment_number=model.default_segment_number,
            flush_interval_sec=model.flush_interval_sec,
            indexing_threshold=model.indexing_threshold,
            max_optimization_threads=model.max_optimization_threads,
            max_segment_size=model.max_segment_size,
            memmap_threshold=model.memmap_threshold,
            payload_indexing_threshold=model.payload_indexing_threshold,
            vacuum_min_vector_number=model.vacuum_min_vector_number,
        )

    @classmethod
    def convert_wal_config(cls, model: http.WalConfig) -> grpc.WalConfigDiff:
        return grpc.WalConfigDiff(
            wal_capacity_mb=model.wal_capacity_mb,
            wal_segments_ahead=model.wal_segments_ahead
        )

    @classmethod
    def convert_distance(cls, model: http.Distance) -> grpc.Distance:
        if model == http.Distance.DOT:
            return grpc.Distance.Dot
        if model == http.Distance.COSINE:
            return grpc.Distance.Cosine
        if model == http.Distance.EUCLID:
            return grpc.Distance.Euclid

        raise ValueError(f"invalid Distance model: {model}")

    @classmethod
    def convert_collection_params(cls, model: http.CollectionParams) -> grpc.CollectionParams:
        return grpc.CollectionParams(
            vector_size=model.vector_size,
            shard_number=model.shard_number,
            distance=cls.convert_distance(model.distance)
        )

    @classmethod
    def convert_optimizers_config_diff(cls, model: http.OptimizersConfigDiff) -> grpc.OptimizersConfigDiff:
        return grpc.OptimizersConfigDiff(
            default_segment_number=model.default_segment_number,
            deleted_threshold=model.deleted_threshold,
            flush_interval_sec=model.flush_interval_sec,
            indexing_threshold=model.indexing_threshold,
            max_optimization_threads=model.max_optimization_threads,
            max_segment_size=model.max_segment_size,
            memmap_threshold=model.memmap_threshold,
            payload_indexing_threshold=model.payload_indexing_threshold,
            vacuum_min_vector_number=model.vacuum_min_vector_number,
        )

    @classmethod
    def convert_update_collection(cls, model: http.UpdateCollection, collection_name: str) -> grpc.UpdateCollection:
        return grpc.UpdateCollection(
            collection_name=collection_name,
            optimizers_config=cls.convert_optimizers_config_diff(
                model.optimizers_config) if model.optimizers_config else None
        )

    @classmethod
    def convert_geo_point(cls, model: http.GeoPoint) -> grpc.GeoPoint:
        return grpc.GeoPoint(
            lon=model.lon,
            lat=model.lat
        )

    @classmethod
    def convert_match(cls, model: http.Match) -> grpc.Match:
        if isinstance(model, http.MatchValue):
            if isinstance(model.value, bool):
                return grpc.Match(boolean=model.value)
            if isinstance(model.value, http.StrictInt):
                return grpc.Match(integer=model.value)
            if isinstance(model.value, http.StrictStr):
                return grpc.Match(keyword=model.value)
        if isinstance(model, http.MatchKeyword):
            return grpc.Match(keyword=model.keyword)
        if isinstance(model, http.MatchInteger):
            return grpc.Match(integer=model.integer)

        raise ValueError(f"invalid Match model: {model}")

    @classmethod
    def convert_alias_operations(cls, model: http.AliasOperations) -> grpc.AliasOperations:
        if isinstance(model, http.CreateAliasOperation):
            return grpc.AliasOperations(create_alias=cls.convert_create_alias(model.create_alias))
        if isinstance(model, http.DeleteAliasOperation):
            return grpc.AliasOperations(delete_alias=cls.convert_delete_alias(model.delete_alias))
        if isinstance(model, http.RenameAliasOperation):
            return grpc.AliasOperations(rename_alias=cls.convert_rename_alias(model.rename_alias))

        raise ValueError(f"invalid AliasOperations model: {model}")

    @classmethod
    def convert_extended_point_id(cls, model: http.ExtendedPointId) -> grpc.PointId:
        if isinstance(model, http.StrictInt):
            return grpc.PointId(num=model)
        if isinstance(model, http.StrictStr):
            return grpc.PointId(uuid=model)
        raise ValueError(f"invalid ExtendedPointId model: {model}")

    @classmethod
    def convert_points_selector(cls, model: http.PointsSelector) -> grpc.PointsSelector:
        if isinstance(model, http.PointIdsList):
            return grpc.PointsSelector(
                points=grpc.PointsIdsList(ids=[cls.convert_extended_point_id(point) for point in model.points])
            )
        raise NotImplementedError()

    @classmethod
    def convert_condition(cls, model: http.Condition) -> grpc.Condition:
        if isinstance(model, http.FieldCondition):
            return grpc.Condition(field=cls.convert_field_condition(model))
        if isinstance(model, http.IsEmptyCondition):
            return grpc.Condition(is_empty=cls.convert_is_empty_condition(model))
        if isinstance(model, http.HasIdCondition):
            return grpc.Condition(has_id=cls.convert_has_id_condition(model))
        if isinstance(model, http.Filter):
            return grpc.Condition(filter=cls.convert_filter(model))

        raise ValueError(f"invalid Condition model: {model}")