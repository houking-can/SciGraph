import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, DeleteView

from .forms import UploadForm
from .models import Post, Operation

from process.extractor import Extractor
from process.converter import Converter
from django.conf import settings


def index(request):
    return render(request, "index.html")


class UserUploadHistoryView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 6
    template_name = "process_user.html"

    def get_queryset(self):
        queryset = Post.objects.all()

        title = self.request.GET.get("title", "")
        startday = self.request.GET.get("startday", "")
        endday = self.request.GET.get("endday", "")

        if title:
            queryset = queryset.filter(title__contains=title)
        if startday:
            queryset = queryset.filter(created__gte=startday)
        if endday:
            queryset = queryset.filter(created__lte=endday)

        return queryset.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            ids = self.request.POST.get("ids", "")
            if ids:
                ids = ids.split(",")
            ids = [int(id) for id in ids]
            Post.objects.filter(pk__in=ids).delete()
            return JsonResponse({"result": True})
        except Exception as e:
            return JsonResponse({"result": False, "message": str(e)})


class AdminUploadHistoryView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 6
    template_name = "process_admin.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["user_list"] = User.objects.filter(is_superuser=False)
        return data

    def post(self, request, *args, **kwargs):
        try:
            ids = self.request.POST.get("ids", "")
            if ids:
                ids = ids.split(",")
            ids = [int(id) for id in ids]
            Post.objects.filter(pk__in=ids).delete()
            return JsonResponse({"result": True})
        except Exception as e:
            return JsonResponse({"result": False, "message": str(e)})


class UserSpecifiedHistoryView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "process_admin.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["user_list"] = User.objects.filter(is_superuser=False)
        return data

    def get_queryset(self):
        queryset = Post.objects.all()
        user = User.objects.get(username=self.request.GET["user"])
        return queryset.filter(user=user)


class UploadPDFView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = UploadForm
    template_name = "upload.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "upload_history_user", kwargs={"username": self.request.user.username}
        )


class PDFOperationView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "detail.html"
    context_object_name = "obj"

    def post(self, request, *args, **kwargs):
        operation = self.request.POST.get("operation", "")
        ids = self.request.POST.get("ids", "")
        input_path = self.get_object().cover.url.lstrip('/')
        base_dir = settings.BASE_DIR
        if operation == "extraction":

            converter = Converter(input=os.path.join(base_dir, input_path),
                                  exe=os.path.join(base_dir, 'process/PDFConvert.exe'),
                                  format='html',
                                  timeout=15,
                                  output=os.path.join(base_dir, 'media/pdf/'))
            html_name = converter.convert()
            if html_name:
                html_dir = os.path.dirname(html_name)
                extractor = Extractor(path=html_dir, file=html_name)
                extractor.get_metadata()
                extractor.get_content()
            else:
                return JsonResponse({"result": False})
            opt = Operation.objects.create(
                type="Metadata Extraction", post=self.get_object()
            )
            opt.save()
            if extractor.has_metadata or extractor.has_content:
                metadata = {"title": extractor.title,
                            "author": extractor.author,
                            "institute": extractor.institute,
                            "journal": extractor.journal,
                            "outline": extractor.outline
                            }
                return JsonResponse({"result": True,
                                     "metadata": metadata,
                                     "content": extractor.content})
            else:
                return JsonResponse({"result": False})

        elif operation == "buildkg":
            path = 'buildkg ' + input_path
            opt = Operation.objects.create(
                type="Build KG", post=self.get_object()
            )
            opt.save()
            return JsonResponse({"result": True, "path": path})

        if ids:
            ids = ids.split(",")
            ids = [int(id) for id in ids]
            Operation.objects.filter(pk__in=ids).delete()
            return JsonResponse({"result": True})


class DeletePDFView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "delete.html"

    def post(self, request, *args, **kwargs):
        try:
            pk = self.request.POST["pk"]
            obj = Post.objects.get(pk=pk)
            try:
                os.remove('media/' + obj.cover.name)
            except:
                pass
            obj.delete()
            return JsonResponse({"result": True})
        except Exception as e:
            return JsonResponse({"result": False, "message": str(e)})


class DeletePDFsView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "delete.html"
    success_url = reverse_lazy("upload_history")

    def post(self, request, *args, **kwargs):
        try:
            ids = self.request.POST.get("ids", "")
            if ids:
                ids = ids.split(",")
            ids = [int(id) for id in ids]
            objs = Post.objects.filter(pk__in=ids)
            for obj in objs:
                try:
                    os.remove('media/' + obj.cover.name)
                except:
                    pass
            objs.delete()
            return JsonResponse({"result": True})
        except Exception as e:
            # return super().post(request, *args, **kwargs)
            return JsonResponse({"result": False, "message": str(e)})


class DeleteOptView(LoginRequiredMixin, DeleteView):
    model = Operation
    template_name = "delete.html"

    def post(self, request, *args, **kwargs):
        try:
            pk = self.request.POST.get("pk", "")
            obj = Operation.objects.get(pk=pk)
            try:
                name, _ = os.path.splitext(obj.post.cover.name)
                os.remove('media/' + name + '.json')
            except:
                pass
            obj.delete()
            return JsonResponse({"result": True})
        except Exception as e:
            return JsonResponse({"result": False, "message": str(e)})


class DeleteOptsView(LoginRequiredMixin, DeleteView):
    model = Operation
    template_name = "delete.html"

    def post(self, request, *args, **kwargs):
        try:
            ids = self.request.POST.get("ids", "")
            if ids:
                ids = ids.split(",")
            ids = [int(id) for id in ids]
            objs = Operation.objects.filter(pk__in=ids)
            for obj in objs:
                try:
                    name, _ = os.path.splitext(obj.post.cover.name)
                    os.remove('media/' + name + '.json')
                except:
                    pass
            objs.delete()
            return JsonResponse({"result": True})
        except Exception as e:
            return JsonResponse({"result": False, "message": str(e)})


class OptHistoryView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "history.html"
    context_object_name = "obj"
