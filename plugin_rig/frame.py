from datetime import datetime
from typing import Any, Dict

import numpy as np

from plugin_rig.util import s2ts


class Frame(Dict[str, Any]):

    @classmethod
    def create(
            cls,
            image: np.ndarray,
            timestamp: float,
            **data: Any) -> 'Frame':

        if image.dtype != np.uint8:
            raise TypeError(f'image must have type uint8 but had type {image.dtype}')
        if image.shape != (1080, 1920, 3):
            raise TypeError(f'image must have shape (1080, 1920, 3) but had {image.shape}')

        f = cls.__new__(cls)
        f.image = image

        f.timestamp = timestamp
        f.timestamp_str = datetime.utcfromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S.') + f'{timestamp % 1 :.2f}'[2:]

        relative_timestamp = data.get('relative_timestamp', timestamp)
        if relative_timestamp is not None:
            f.relative_timestamp_str = f'{s2ts(relative_timestamp)}.' + f'{relative_timestamp % 1 :.2f}'[2:]

        f.update(data)
        return f

    @property
    def debug(self) -> bool:
        return self.get('debug_image') is not None

    def strip(self) -> 'Frame':
        """
        Remove all top-level numpy arrays
        """
        for k in 'image', 'debug_image':
            if k in self:
                del self[k]
        for k in list(self.keys()):
            if isinstance(self.get(k), np.ndarray):
                del self[k]
        return self

    def copy(self) -> 'Frame':
        return Frame(**self)

    def __getattr__(self, item: str) -> Any:
        if item not in self:
            raise AttributeError('Frame does not (yet?) have attribute %r' % (item,))
        return self[item]

    def __setattr__(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            raise ValueError(f'Cannot add item "{key}": already exists')
        super().__setitem__(key, value)

