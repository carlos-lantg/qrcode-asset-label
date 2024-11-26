
# QRcode Asset Label Generator

Simple API to generate labels for assets


## Demo

https://qrcode-asset-label.onrender.com/generate_label/?code=12345&width_mm=50&height_mm=30&font_size=12


## API Reference

#### Generate Label

```http
  GET /generate_label/?code={code}&width_mm={width_mm}&height_mm={height_mm}&font_size={font_size}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `code`      | `string` | **Required**. content|
| `width_mm`  | `string` | **Required**. width |
| `height_mm` | `string` | **Required**. height |
| `font_size` | `string` | **Required**. font size|



