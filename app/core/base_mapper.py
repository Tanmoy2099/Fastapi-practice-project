from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DTOType = TypeVar("DTOType")
DomainType = TypeVar("DomainType")


class BaseMapper(ABC, Generic[DTOType, DomainType]):
    """
    Abstract Base Class for mapping API payloads (DTOs)
    to internal business logic representations (Domain models).
    """

    @staticmethod
    @abstractmethod
    def to_domain(dto: DTOType) -> DomainType:
        """Convert a Data Transfer Object to a pure Domain model"""
        pass

    @staticmethod
    @abstractmethod
    def to_dto(domain: DomainType) -> DTOType:
        """Convert a Domain model back to a Data Transfer Object"""
        pass
