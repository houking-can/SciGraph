from django.urls import path
from . import views
from .views import (
    UploadPDFView,
    UserUploadHistoryView,
    AdminUploadHistoryView,
    UserSpecifiedHistoryView,
    ImageOperationView,
    DeletePDFView,
    DeletePDFsView,
    DeleteOptView,
)


urlpatterns = [
    path("", views.index, name="papers_index"),
    path("upload/", UploadPDFView.as_view(), name="upload_pdf"),
    path(
        "process/history/user/<username>/",
        UserUploadHistoryView.as_view(),
        name="upload_history_user",
    ),
    path(
        "process/history/admin/<adminname>/",
        AdminUploadHistoryView.as_view(),
        name="upload_history_admin",
    ),
    path(
        "process/history/admin/<adminname>/specified/",
        UserSpecifiedHistoryView.as_view(),
        name="upload_history_specified",
    ),
    path("process/detail/<pk>/", ImageOperationView.as_view(), name="detail"),
    path("process/delete/image/<pk>/", DeletePDFView.as_view(), name="delete_image"),
    path("process/delete/images/", DeletePDFsView.as_view(), name="delete_images"),
    path(
        "process/delete/operation/<pk>", DeleteOptView.as_view(), name="delete_opt"
    ),
]
