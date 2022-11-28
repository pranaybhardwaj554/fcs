from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .form import DocumentForm, ShareForm
from .models import Doc, Share 
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from authenticate.models import User
from request.models import Keys 
import base64
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
@login_required(login_url = "/login")
def upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        print(request.user)
        if form.is_valid():
            doc = Doc.objects.create(author = request.user, description = form.cleaned_data['description'], document = form.cleaned_data['document']) 
            doc.save()
            return redirect('/dashboard')
        else:
            return render(request, '../templates/upload.html', {'form': form})
    return render(request, "../templates/upload.html")

@login_required(login_url = "/login")
def share_docs(request):
    if request.method == 'POST' :
        form = ShareForm(request.POST, request.FILES)
        # print(request.user)
        # print('cfgv')
        # print(form.is_valid())
        if form.is_valid() and request.FILES['document']:
            # print("hello")
            file_name = request.FILES['document']
            string = file_name.read()
            m = SHA256.new(string)
            me = Keys.objects.all().filter(user__exact = request.user)
            private_key = me[0].private_key
            private_key = RSA.import_key(private_key)
            sign = pkcs1_15.new(private_key)
            signature = sign.sign(m)
            save = ""
            for i in signature:
                save = save + str(i) + " "
            save = save[:-1]
            # print(sign)
            doc = Share.objects.create(shared_to = form.cleaned_data['shared_to'], author = request.user, description = form.cleaned_data['description'], document = form.cleaned_data['document'], digital_sign = save, doc_type = form.cleaned_data['doc_type'])
            doc.save()
            return redirect('/dashboard')
        else:
            return render(request, '../templates/share_docs.html', {'form': form})
    return render(request, "../templates/share_docs.html")

class UserPostListView(ListView):
    model = Doc
    template_name = 'user_posts.html'
    context_object_name = 'posts'
   
    def get_queryset(self):
        print(self.request.user)
        lis = (Doc.objects.filter(author=self.request.user)) 
        print(len(lis))
        return Doc.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doc
    success_url = '/'
    template_name = 'post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        # print(post)
        # print(post.document.storage.exists(post.document.name))

        post.document.storage.delete(post.document.name)
        # print(post.document.storage.exists(post.document.name))
        if self.request.user == post.author:
            return True
        return False

class SharedByMe(ListView):
    model = Share
    template_name = 'shared_by_me.html'
    context_object_name = 'files'
   
    def get_queryset(self):
        # print(self.request.user)
        # lis = (Doc.objects.filter(author=self.request.user)) 
        # print(len(lis))
        return Share.objects.filter(author=self.request.user)

class SharedWithMe(ListView):
    model = Share
    template_name = 'shared_with_me.html'
    context_object_name = 'shared'
   
    def get_queryset(self):
        # print(self.request.user)
        # lis = (Doc.objects.filter(author=self.request.user)) 
        # print(len(lis))
        print(self.request.user.email)
        return Share.objects.filter(shared_to=self.request.user.email)