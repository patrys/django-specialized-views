django-specialized-views
========================

Func-based views

```python
# …
from specialized_views import view


@view
def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return {
        'product': product,
        'template': 'product/details.html'}


# custom mime renderer
@product_details.for_mime('application/json')
def product_json(request, response, **kwargs):
    product = response['product']
    return json.dumps({
        'name': product.name,
        'price': product.price})


# custom AJAX handler
@product_details.for_ajax
def product_ajax(request, response, **kwargs):
    return dict(response, template='product/ajax.html')
```
