# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python libs
import hashlib
# Django packages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, ListView
# Our Models
from .forms import NewPrescriptionForm
from .models import Prescription, Block
from .utils import get_qr_code



class AddPrescriptionView(View):
    ''' Simple Rx Form '''
    template = 'blockchain/blockchain/new_rx.html'

    def get(self, request, *args, **kwargs):
        template = 'blockchain/new_rx.html'
        form = NewPrescriptionForm
        return render(request, template ,{"form": form,})

    def post(self, request, *args, **kwargs):
        template = 'blockchain/new_rx.html'
        form = NewPrescriptionForm(request.POST)
        if form.is_valid():
            rx = form.save(commit = False)
            rx.save()
            hash_object = hashlib.sha256(str(rx.timestamp))
            rx.signature = hash_object.hexdigest()
            rx.save()

        return redirect('/')


def rx_detail(request, hash_rx=False):
    ''' Get a hash and return the rx '''
    if request.GET.get("hash_rx", False):
        hash_rx = request.GET.get("hash_rx")

    if hash_rx:
        context = {}
        try:
            rx = Prescription.objects.get(signature=hash_rx)
            medications = get_simplified_medication_json(rx.medications.all())
            context["rx"] = rx
            context["medications"] = medications
            return render(request, "blockchain/rx_detail.html", context)

        except Exception as e:
            # Add logger here
            return redirect("/block/?block_hash=%s" % hash_rx)

    return redirect("/")


def rx_priv_key(request, hash_rx=False):
    # Temporary way to show key just for test, remove later
    try:
        rx = Prescription.objects.get(signature=hash_rx)
        return HttpResponse(rx.get_priv_key, content_type="text/plain")
    except Exception as e:
        return HttpResponse("Not Found", content_type="text/plain")


def qr_code(request, hash_rx=False):
    # Temporary way to show qrcode just for test, remove later
    try:
        rx = Prescription.objects.get(signature=hash_rx)
        img = get_qr_code(rx.get_priv_key)
        return HttpResponse(img, content_type="image/jpeg"
)
    except Exception as e:
        print("Error :%s, type(%s)" % (e, type(e)))
        return HttpResponse("Not Found", content_type="text/plain")



def block_detail(request, block_hash=False):
    ''' Get a hash and return the block '''
    if request.GET.get("block_hash", False):
        block_hash = request.GET.get("block_hash")

    if block_hash:
        context = {}
        try:
            block = Block.objects.get(hash_block=block_hash)
            context["block_object"] = block
            return render(request, "blockchain/block_detail.html", context)

        except Exception as e:
            print("Error found: %s, type: %s" % (e, type(e)))

    return redirect("/")

def get_simplified_medication_json(medications):
    medication_json = []
    for medication in medications:
        json = {}
        json['instructions'] = medication.instructions
        json['presentation'] = medication.presentation
        medication_json.append(json)
    return medication_json[::-1] # This 'pythonesque' code reverts order of lists
