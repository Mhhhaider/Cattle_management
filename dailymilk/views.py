from django.shortcuts import render, redirect, get_object_or_404
from .models import Farmer, MilkCollection
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib import messages

def customers_list(request):
    customers = Farmer.objects.all().order_by('-id')
    return render(request, 'customer_list.html', {
        'customers':customers,
    })



def customers_add(request):
    if request.method == 'POST':
        cardno = request.POST.get('cardno')
        name = request.POST.get('name')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        # Check if cardno already exists
        if Farmer.objects.filter(cardno=cardno,name=name).exists():
            messages.error(request, "Card Number already exists, please use another.")
            return render(request, 'customer_form.html', {
                'cardno': cardno,
                'name': name,
                'phone': phone,
                'address': address
            })

        # Create new customer
        Farmer.objects.create(
            cardno=cardno,
            name=name,
            phone=phone,
            address=address
        )
        messages.success(request, "Customer added successfully!")
        return redirect('customer-list')

    return render(request, 'customer_form.html')



def customers_list(request):
    customers = Farmer.objects.all().order_by('-id')
    return render(request, 'customer_list.html', {
        'customers':customers,
    })


def customers_delete(request,id):
    customers = Farmer.objects.get(pk=id)
    customers.delete()
    return redirect('customer-list')
    

# =============================Daily Milk Collections=============================#

def collection_add(request):
    farmers = Farmer.objects.all()  # to show card numbers

    if request.method == "POST":
        cardno = request.POST.get("cardno")         # selected card no
        farmer = request.POST.get("farmer")    # manual input
        date = request.POST.get("date")
        shift = request.POST.get("shift")
        type = request.POST.get("type")
        payment = request.POST.get("payment")
        qty = float(request.POST.get("quantity_ltr"))
        rate = float(request.POST.get("rate_per_ltr"))

        amount = qty * rate

        MilkCollection.objects.create(
            cardno=cardno,
            farmer=farmer,
            date=date,
            shift=shift,
            quantity_ltr=qty,
            rate_per_ltr=rate,
            type=type,
            payment=payment,
            amount=amount
        )

        messages.success(request, "Milk collection added successfully")
        return redirect("collection_list")

    return render(request, "daily_milk.html", {"farmers": farmers})

def collection_list(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    farmer = request.GET.get("farmer")
    cardno = request.GET.get("cardno")

    collections = MilkCollection.objects.all().order_by('-date')

    # Apply Filters
    if from_date:
        collections = collections.filter(date__gte=from_date)

    if to_date:
        collections = collections.filter(date__lte=to_date)

    if farmer:
        collections = collections.filter(farmer__icontains=farmer)

    if cardno:
        collections = collections.filter(cardno__icontains=cardno)

    # Summary
    total_qty = collections.aggregate(Sum('quantity_ltr'))['quantity_ltr__sum'] or 0
    total_amount = collections.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, "dailymilk_list.html", {
        "collections": collections,
        "total_qty": total_qty,
        "total_amount": total_amount,
    })



def collection_edit(request, pk):
    obj = get_object_or_404(MilkCollection, pk=pk)
    farmers = Farmer.objects.all()

    if request.method == "POST":
        obj.farmer_id = int(request.POST.get("farmer"))
        obj.date = request.POST.get("date")
        obj.shift = request.POST.get("shift")

        obj.quantity_ltr = float(request.POST.get("quantity_ltr"))
        obj.fat = request.POST.get("fat")
        obj.rate_per_ltr = float(request.POST.get("rate_per_ltr"))

        obj.amount = obj.quantity_ltr * obj.rate_per_ltr
        obj.save()

        return redirect("collection_list")

    return render(request, "daily_milk.html", {"farmers": farmers, "obj": obj})


def collection_delete(request, pk):
    obj = get_object_or_404(MilkCollection, pk=pk)
    obj.delete()
    return redirect('collection_list')




# PDF Generation
def collection_pdf(request):
    collections = MilkCollection.objects.all().order_by('-date')

    # Apply same filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    farmer_name = request.GET.get('farmer_name')

    if from_date:
        collections = collections.filter(date__gte=from_date)
    if to_date:
        collections = collections.filter(date__lte=to_date)
    if farmer_name:
        collections = collections.filter(farmer__name__icontains=farmer_name)

    total_qty = collections.aggregate(Sum('quantity_ltr'))['quantity_ltr__sum'] or 0
    total_amount = collections.aggregate(Sum('amount'))['amount__sum'] or 0

    template_path = 'collection_pdf.html'
    context = {
        'collections': collections,
        'total_qty': total_qty,
        'total_amount': total_amount,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="milk_collections.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF <pre>" + html + "</pre>")
    return response
    
    