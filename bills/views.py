# billing/views.py
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Bill
from django.shortcuts import render, redirect,get_object_or_404
from .models import Customer, Item, Bill, BillItem
from django.contrib import messages
from .models import Item

def create_bill(request):
    items = Item.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        selected_items = request.POST.getlist("items")
        payment=request.POST.get("payment")
        cardno=request.POST.get("cardno")

        customer = get_object_or_404(Customer, id=customer_id)
        bill = Bill.objects.create(customer=customer)

        for item_id in selected_items:
            item = get_object_or_404(Item, id=item_id)
            quantity_str = request.POST.get(f"quantities_{item.id}", "0")
            
            try:
                quantity = float(quantity_str)  # fractional quantity allowed
            except ValueError:
                quantity = 0

            if quantity > 0:
                BillItem.objects.create(bill=bill, item=item, quantity=quantity, payment=payment, cardno=cardno)

        return redirect('view_bill', bill_id=bill.id)

    return render(request, 'create_bill.html', {'items': items, 'customers': customers})

def view_bill(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    return render(request, 'view_bill.html', {'bill': bill})


def billitem_list(request):
    items = BillItem.objects.all()

    bill_no = request.GET.get("bill_no")
    customer = request.GET.get("customer")
    date = request.GET.get("date")   # yyyy-mm-dd format

    if bill_no:
        items = items.filter(bill__id=bill_no)

    if customer:
        items = items.filter(bill__customer__name__icontains=customer)

    if date:
        items = items.filter(bill__date__date=date)

    return render(request, 'billitem_list.html', {'items': items})





def download_bill_pdf(request, bill_id):
    bill = Bill.objects.get(id=bill_id)

    template_path = 'bill_pdf_template.html'
    context = {'bill': bill}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation error')

    return response






def add_item(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        unit = request.POST.get("unit")

        if name and price and stock and unit:
            try:
                price = float(price)
                stock = int(stock)
                Item.objects.create(name=name, price=price, stock=stock, unit=unit)
                messages.success(request, f"Item '{name}' added successfully!")
                return redirect('add_item')  # Redirect to same page
            except Exception as e:
                messages.error(request, f"Error: {e}")
        else:
            messages.error(request, "All fields are required!")

    return render(request, "add_item.html")


def item_list(request):
    items = Item.objects.all()
    return render(request, "item_list.html", {"items": items})

def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    messages.success(request, f"Item '{item.name}' deleted successfully!")
    return redirect("item_list")


# Add Customer
def add_customer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        Customer.objects.create(name=name, phone=phone)
        return redirect('create_bill')
    return render(request, 'add_customer.html')

# List Customers
def list_customers(request):
    customers = Customer.objects.all()
    return render(request, 'list_customers.html', {'customers': customers})