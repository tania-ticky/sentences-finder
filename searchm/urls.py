from django.urls import path
from searchm import views
urlpatterns = [

    path('search/', views.search_word,name='index2'),
    #path('form/', views.form_view,name='form'),
    path('favorite/', views.extract_fav,name='favorites'),
    path('fav/', views.fav,name='fav'),
    path('del/', views.del_sen_req,name='deleteSentence'),
    path('b/', views.printmore,name='index1'),
]
