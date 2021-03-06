from django.urls import path
from . import views
from .views import (
    UploadPDFView,
    UserUploadHistoryView,
    AdminUploadHistoryView,
    UserSpecifiedHistoryView,
    PreviewView,
    DeletePDFView,
    DeletePDFsView,
    DeleteOptView,
    DeleteOptsView,
    OptHistoryView,
    MetadataView,
    BuildKGView

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
    path("process/preview/<pk>/", PreviewView.as_view(), name="preview"),
    path("process/delete/PDF/<pk>/", DeletePDFView.as_view(), name="delete_pdf"),
    path("process/delete/PDF/", DeletePDFsView.as_view(), name="delete_pdfs"),
    path("process/delete/operation/<pk>", DeleteOptView.as_view(), name="delete_opt"),
    path("process/delete/operation/", DeleteOptsView.as_view(), name="delete_opts"),
    path("process/opt_history/<pk>/", OptHistoryView.as_view(), name="opt_history"),
    path("process/metadata/<pk>/", MetadataView.as_view(), name="metadata"),
    path("process/build_kg/<pk>/", BuildKGView.as_view(), name="build_kg")
]
