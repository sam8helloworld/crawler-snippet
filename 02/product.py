from dataclasses import dataclass

@dataclass
class Product:
    sku: str
    url: str
    price: str
    image_url: str

    def __init__(
        self,
        sku: str,
        url: str,
        price: str,
        image_url: str,
    ):
        self.sku = sku
        self.url = url
        self.price = price
        self.image_url = image_url
    
    def to_json(self) -> dict:        
        data = {
            "管理番号": "",
            "SKU": self.sku,
            "シーインURL": self.url,
            "シーイン画像": self.image_url,
            "サイズ": "",
            "価格": self.price,
            "アマゾンURL": "",
            "アマゾン画像": "",
            "価格2": "",
        }
        return data