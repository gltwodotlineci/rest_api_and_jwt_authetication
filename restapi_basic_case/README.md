


________
### Installing dependences Rest

``` bash
pip install djangorestframework==3.12.4
```
In settings
```python
INSTALLED_APPS = [
'rest_framework',
]
```
In url


```python
urlpatterns = [
    path('api-auth/', include('rest_framework.urls'))
]
```


### Authentification API dependences

``` bash
pip install djangorestframework_simplejwt
```
