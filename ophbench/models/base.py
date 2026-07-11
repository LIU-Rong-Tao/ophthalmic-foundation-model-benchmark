from abc import ABC, abstractmethod


class BaseModelAdapter(ABC):
    model_id: str
    capabilities: tuple[str, ...]

    @abstractmethod
    def check_environment(self): ...

    @abstractmethod
    def load(self): ...


class ImageEncoderAdapter(BaseModelAdapter):
    @abstractmethod
    def preprocess(self, image): ...

    @abstractmethod
    def encode_image(self, image): ...


class VisionLanguageAdapter(BaseModelAdapter):
    @abstractmethod
    def preprocess_image(self, image): ...

    @abstractmethod
    def encode_image(self, image): ...

    @abstractmethod
    def encode_text(self, text): ...

    @abstractmethod
    def zero_shot_predict(self, image, labels): ...


class SegmentationAdapter(BaseModelAdapter):
    @abstractmethod
    def predict_mask(self, image): ...


class GenerativeAdapter(BaseModelAdapter):
    @abstractmethod
    def generate(self, inputs): ...
