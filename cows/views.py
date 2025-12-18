import pandas as pd
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, date
from .models import *
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import calendar
# Create your views here.

# @login_required(login_url="log-in")
# def cow_home(request):
#     total_cattles = Cattle.objects.count()
#     context={'total_cattles':total_cattles}
#     return render(request,'home-page.html',context)


@login_required(login_url="log-in")
def cow_home(request):
    total_cattles = Cattle.objects.count()
    total_milk = Milking.objects.aggregate(total=Sum('amount'))['total'] or 0
    health = HealthStatus.objects.count()
    feed = FeedStock.objects.count()
    income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
    today = date.today()

    # 1️⃣ Missed / expired convincing dates
    missed_convincing = Cattle.objects.filter(
        convincing_date__lte=today
    ).exclude(convincing_date=None).order_by('convincing_date')

    # 2️⃣ Near expiry convincing dates (next 3 days)
    near_expiry_convincing = Cattle.objects.filter(
        convincing_date__gt=today,
        convincing_date__lte=today + timedelta(days=3)
    ).order_by('convincing_date')
    data = {
        'fresh': Cattle.objects.filter(breeding='Fresh').count(),
        'pregnant': Cattle.objects.filter(breeding='Pregnant').count(),
        'dry': Cattle.objects.filter(breeding='Dry').count(),
        'inseminated': Cattle.objects.filter(breeding='Inseminated').count(),
    }
    milkings = Milking.objects.all().order_by('-date')

    # Aggregate total milk per month
    month_totals_qs = (
        milkings
        .annotate(month=ExtractMonth('date'))  # extract month from date
        .values('month')
        .annotate(total=Sum('amount'))  # sum milk for the month
        .order_by('month')
    )

    # Prepare lists for chart
    months = []
    monthly_totals = []
    month_map = {i: calendar.month_abbr[i] for i in range(1, 13)}  # 1->Jan, 2->Feb, ...

    for m in range(1, 13):
        month_data = next((x for x in month_totals_qs if x['month'] == m), None)
        months.append(month_map[m])
        monthly_totals.append(month_data['total'] if month_data else 0)


    # Count for Alerts
    missed_count = Cattle.objects.filter(
    convincing_date__lte=today
    ).exclude(convincing_date=None).count()

    near_expiry_count = Cattle.objects.filter(
    convincing_date__gt=today,
    convincing_date__lte=today + timedelta(days=3)
    ).count()

    total_count = missed_count + near_expiry_count
    context = {
        'missed_convincing': missed_convincing,
        'near_expiry_convincing': near_expiry_convincing,
        'total_cattles':total_cattles,
        'data':data,
        'milkings': milkings,
        'months': months,            # ['Jan', 'Feb', ...]
        'monthly_totals': monthly_totals,  # [150, 200, 0, ...]
        'total_count':total_count,
        'health':health,
        'feed':feed,
        'total_milk':total_milk,
        'income':income,
    }

    return render(request, 'home-page.html', context)


def safe_decimal(value):
    try:
        if value is None:
            return None
        
        if isinstance(value, str):
            v = value.strip().replace("“", "").replace("”", "")
            if v in ["", "-", "null", "none", "None"]:
                return None
            return Decimal(v)

        return Decimal(str(value))

    except:
        return None

def safe_int(value, default=None):
    try:
        if value in [None, "", " "]:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_date(value):
    """
    Converts value to a date object.
    Returns None if value is blank or invalid.
    """
    from datetime import datetime, date
    if value in [None, "", " "]:
        return None
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except:
        return None

# ------------------------------
# Add Cattle View
# ------------------------------
@login_required(login_url="log-in")
def add_cattle(request):
    batches = Batch.objects.all()

    if request.method == 'POST':

        # -------------------------------
        # EXCEL FILE UPLOAD
        # -------------------------------
        if "excel_file" in request.FILES:
            excel_file = request.FILES["excel_file"]
            try:
                df = pd.read_excel(excel_file)

                # Normalize columns: remove spaces, smart quotes, lowercase
                df.columns = df.columns.str.strip().str.replace("“","").str.replace("”","")
                df.columns = [col.lower() for col in df.columns]

                # Map Excel columns to model fields
                df.rename(columns={
                    'batch': 'batch',
                    'batch name': 'batch',
                    'tag name': 'name',
                    'name': 'name',
                    'age': 'age',
                    'breed': 'breed',
                    'milk': 'milk',
                    'purchase': 'purchase',
                    'purchase amount': 'purchase_amount',
                    'breeding': 'breeding',
                    'health status': 'health_status',
                    'health': 'health_status',
                    'convincing date': 'convincing_date',
                    'result': 'result',
                    'milk day 15': 'milk_day_15',
                    'milk day 30': 'milk_day_30',
                    'milk day 60': 'milk_day_60',
                    'milk day 75': 'milk_day_75',
                    'outward date': 'outward_date',
                    'sale date': 'sale_date',
                    'sold': 'sold',
                    'salvage date': 'salvage_date',
                    'salvage': 'salvage',
                }, inplace=True)

                # Required columns
                required_cols = ['batch', 'name', 'age', 'breed', 'health_status']
                for col in required_cols:
                    if col not in df.columns:
                        messages.error(request, f"Excel column '{col}' missing!")
                        return redirect('add_cattle')

                # Loop through rows
                for index, row in df.iterrows():
                    batch_name = row['batch']
                    if not batch_name:  # Check blank batch
                        messages.error(request, f"Batch missing at row {index+2}")
                        continue
                    try:
                        batch = Batch.objects.get(name=batch_name)
                    except Batch.DoesNotExist:
                        messages.error(request, f"Batch '{batch_name}' not found (Row {index+2})")
                        continue

                    # Create cattle safely
                    Cattle.objects.create(
                        batch=batch,
                        name=row['name'],
                        age=safe_int(row['age']),
                        breed=row.get('breed', ''),
                        milk=safe_decimal(row.get('milk')),
                        purchase=safe_date(row.get('purchase')),
                        purchase_amount=safe_decimal(row.get('purchase_amount')),
                        breeding=row.get('breeding', ''),
                        health_status=row['health_status'],
                        convincing_date=safe_date(row.get('convincing_date')),
                        result=row.get('result', ''),
                        milk_day_15=safe_decimal(row.get('milk_day_15')),
                        milk_day_30=safe_decimal(row.get('milk_day_30')),
                        milk_day_60=safe_decimal(row.get('milk_day_60')),
                        milk_day_75=safe_decimal(row.get('milk_day_75')),
                        outward_date=safe_date(row.get('outward_date')),
                        sale_date=safe_date(row.get('sale_date')),
                        sold=safe_decimal(row.get('sold')),
                        salvage_date=safe_date(row.get('salvage_date')),
                        salvage=row.get('salvage', '')
                    )

                messages.success(request, "Excel imported successfully!")
                return redirect('cattle_list')

            except Exception as e:
                messages.error(request, f"Error importing Excel: {e}")
                return redirect('add_cattle')

        # -------------------------------
        # SINGLE FORM SUBMISSION
        # -------------------------------
        else:
            batch_id = request.POST.get('batch')
            try:
                batch = Batch.objects.get(id=batch_id)
            except Batch.DoesNotExist:
                messages.error(request, f"Batch ID '{batch_id}' does not exist.")
                return redirect('cattle_list')

            Cattle.objects.create(
                batch=batch,
                name=request.POST.get('name'),
                age=safe_int(request.POST.get('age')),
                breed=request.POST.get('breed', ''),
                milk=safe_decimal(request.POST.get('milk')),
                purchase=safe_date(request.POST.get('purchase')),
                purchase_amount=safe_decimal(request.POST.get('purchase_amount')),
                breeding=request.POST.get('breeding', ''),
                health_status=request.POST.get('health_status'),
                convincing_date=safe_date(request.POST.get('convincing_date')),
                result=request.POST.get('result', ''),
                milk_day_15=safe_decimal(request.POST.get('milk_day_15')),
                milk_day_30=safe_decimal(request.POST.get('milk_day_30')),
                milk_day_60=safe_decimal(request.POST.get('milk_day_60')),
                milk_day_75=safe_decimal(request.POST.get('milk_day_75')),
                outward_date=safe_date(request.POST.get('outward_date')),
                sale_date=safe_date(request.POST.get('sale_date')),
                sold=safe_decimal(request.POST.get('sold')),
                salvage_date=safe_date(request.POST.get('salvage_date')),
                salvage=request.POST.get('salvage', '')
            )

            messages.success(request, "Cattle added successfully!")
            return redirect('cattle_list')

    # GET request
    return render(request, 'cattle/add_cattle.html', {'batches': batches})


#---------------------------
# List Cattle
#---------------------------
def cattle_list(request):
    status = request.GET.get('status')
    
    # Initial queryset: conditionally set is_archive
    if status in ["Sold", "Salvage"]:
        cattles = Cattle.objects.filter(is_archive=True)
    else:
        cattles = Cattle.objects.filter(is_archive=False)

    # Filters
    name = request.GET.get('name')
    batch = request.GET.get('batch')
    health_status = request.GET.get('health_status')

    if name:
        cattles = cattles.filter(name__icontains=name)

    if batch:
        cattles = cattles.filter(batch_id=batch)

    if status:
        if status in ["Fresh", "Inseminated", "Pregnant", "Dry"]:
            cattles = cattles.filter(breeding=status)
        elif status == "Sold":
            cattles = cattles.filter(sold__isnull=False)  # sold wali condition
        elif status == "Salvage":
            cattles = cattles.filter(salvage__isnull=False)  # salvage wali condition

    if health_status:
        cattles = cattles.filter(health_status=health_status)

    batches = Batch.objects.all()
    health_choices = Cattle.HEALTH_CHOICES
    today = date.today()

    context = {
        'cattles': cattles,
        'batches': batches,
        'health_choices': health_choices,
        'status': status,
        'today': today,
    }

    return render(request, 'cattle/cattle_list.html', context)

#---------------------------
# List Cattle Sale
#---------------------------
def sell_cattle(request, id):
    cattle = get_object_or_404(Cattle, id=id)

    if request.method == "POST":
        cattle.sale_date = request.POST.get("sale_date")
        cattle.sold = safe_decimal(request.POST.get("sold")) 
        cattle.salvage = request.POST.get("salvage")
        cattle.is_archive = True      # ARCHIVE FLAG
        cattle.save()

        messages.success(request, "Cattle Sold & Archived Successfully!")
        return redirect("cattle_list")

#---------------------------
# List Cattle Archive
#---------------------------
def cattle_archive(request):
    cattles = Cattle.objects.filter(is_archive=True)
    return render(request, "cattle/archive_list.html", {
        "cattles": cattles
    })



#-----------------------------
# Re-Entry Cattle
#-----------------------------
def reentry_cattle(request, cattle_id):
    old_cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == "POST":
        # Create new cattle entry
        new_cattle = Cattle.objects.create(
            name=request.POST['name'],
            batch_id=request.POST['batch'],
            age=request.POST['age'],
            breed=request.POST['breed'],
            milk=request.POST['milk'] or 0,
            purchase=request.POST['purchase'],
            purchase_amount=request.POST['purchase_amount'],
            breeding=request.POST['breeding'],
            health_status=request.POST['health_status'],
            milk_day_15=request.POST.get('milk_day_15') or 0,
            milk_day_30=request.POST.get('milk_day_30') or 0,
            milk_day_60=request.POST.get('milk_day_60') or 0,
            milk_day_75=request.POST.get('milk_day_75') or 0,
        )

        # Mark OLD cattle
        old_cattle.reentered = True
        old_cattle.save()

        # Mark NEW cattle also
        new_cattle.reentered = True
        new_cattle.save()

        messages.success(request, f"Cattle {new_cattle.name} re-entered successfully!")
        return redirect('cattle_list')

    batches = Batch.objects.all()
    health_choices = Cattle.HEALTH_CHOICES

    return render(request, 'cattle/reentry_form.html', {
        'old_cattle': old_cattle,
        'batches': batches,
        'health_choices': health_choices,
    })

#-----------------------------
# Add Milking
#-----------------------------
def add_milking(request):
    cattles = Cattle.objects.all()
    if request.method == 'POST':
        cattle_id = request.POST.get('cattle')
        milk_date = request.POST.get('date')
        milk_time = request.POST.get('milk_time')
        amount = request.POST.get('amount')

        cattle = Cattle.objects.get(id=cattle_id)
        Milking.objects.create(cattle=cattle, date=milk_date,milk_time=milk_time, amount=amount)
        return redirect('milking_list')

    today = date.today()
    return render(request, 'milk/add_milking.html', {'cattles': cattles, 'today': today})

# List Milking
def milking_list(request):
    milkings = Milking.objects.all()
    return render(request, 'milk/milking_list.html', {'milkings': milkings})

# Milk Report
def cattle_milk_report(request):
    cattles = Cattle.objects.all()
    milk_report = []
    for cattle in cattles:
        total_milk = sum(m.amount for m in cattle.milkings.all())
        milk_report.append({
            'name': cattle.name,
            'batch': cattle.batch.name,
            'total_milk': total_milk
        })
    return render(request, 'cattle_milk_report.html', {'milk_report': milk_report})


# Add Herd Inventory
def add_inventory(request):
    cattles = Cattle.objects.all()
    if request.method == 'POST':
        cattle_id = request.POST.get('cattle')
        batch_no = request.POST.get('batch_no')
        inward_date = request.POST.get('inward_date')
        convincing_date = request.POST.get('convincing_date')
        result = request.POST.get('result')
        milk_day_0 = request.POST.get('milk_day_0')
        milk_day_15 = request.POST.get('milk_day_15')
        milk_day_30 = request.POST.get('milk_day_30')
        milk_day_60 = request.POST.get('milk_day_60')
        milk_day_75 = request.POST.get('milk_day_75')
        outward_date = request.POST.get('outward_date')
        sale_date = request.POST.get('sale_date')

        cattle = Cattle.objects.get(id=cattle_id)

        BatchInventory.objects.create(
            cattle=cattle,
            batch_no=batch_no,
            inward_date=inward_date,
            convincing_date=convincing_date,
            result=result,
            milk_day_0=milk_day_0,
            milk_day_15=milk_day_15,
            milk_day_30=milk_day_30,
            milk_day_60=milk_day_60,
            milk_day_75=milk_day_75,
            outward_date=outward_date,
            sale_date=sale_date
        )

        return redirect('inventory_list')

    today = date.today()
    return render(request, 'add_inventory.html', {'cattles': cattles, 'today': today})


#Herd Inventory List
def inventory_list(request):
    records = BatchInventory.objects.all().order_by('-inward_date')
    today = date.today()   # Current date
    context = {
        'records': records,
        'today': today,
    }
    return render(request, 'inventory_list.html', context)


# Add Breeding
def add_breeding(request):
    if request.method == 'POST':
        male_id = request.POST.get('male_cattle')
        female_id = request.POST.get('female_cattle')
        breeding_date = request.POST.get('breeding_date')
        delivery_date = request.POST.get('expected_delivery_date')
        notes = request.POST.get('notes')

        # Save Record
        Breeding.objects.create(
            male_cattle_id=male_id,
            female_cattle_id=female_id,
            breeding_date=breeding_date,
            expected_delivery_date=delivery_date,
            notes=notes
        )

        # ===== DELIVERY DATE NEAR MESSAGE =====
        if delivery_date:
            d_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
            today = datetime.today().date()
            diff = (d_date - today).days

            if 0 <= diff <= 7:
                messages.warning(request, "⚠ Delivery date is very near! Please check the cattle.")

        return redirect('breeding-list')

    # Send cattles to HTML
    male_cattles = Cattle.objects.filter(breed__icontains='bull')
    female_cattles = Cattle.objects.exclude(breed__icontains='bull')

    return render(request, "breeding/add_breeding.html", {
        "male_cattles": male_cattles,
        "female_cattles": female_cattles,
    })


# Breeding List
def breeding_list(request):
    today = datetime.today().date()

    breedings = Breeding.objects.all()

    data = []

    for b in breedings:
        warning = ""
        if b.expected_delivery_date:
            diff = (b.expected_delivery_date - today).days

            if diff < 0:
                warning = "❌ Delivery Date missed!"
            elif 0 <= diff <= 7:
                warning = "⚠ Delivery Date is near!"

        data.append({
            "male": b.male_cattle,
            "female": b.female_cattle,
            "breeding_date": b.breeding_date,
            "delivery_date": b.expected_delivery_date,
            "notes": b.notes,
            "warning": warning
        })

    return render(request, "breeding/breeding_list.html", {"breedings": data})

# Health Status
def add_health_status(request):
    batches = Batch.objects.all()
    cattles = Cattle.objects.all()

    if request.method == 'POST':
        batch_id = request.POST.get('batch')
        cattle_id = request.POST.get('cattle')
        vaccination_date = request.POST.get('vaccination_date')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        batch = Batch.objects.get(id=batch_id)
        cattle = Cattle.objects.get(id=cattle_id)

        HealthStatus.objects.create(
            batch=batch,
            cattle=cattle,
            vaccination_date=vaccination_date,
            status=status,
            notes=notes
        )
        return redirect('health_status_list')

    return render(request, 'health/health_status.html', {'batches': batches, 'cattles': cattles})


# Health Status List
def health_status_list(request):
    records = HealthStatus.objects.all().order_by('-vaccination_date')
    return render(request, 'health/health_list.html', {'records': records})


# Add Breed
def add_feed(request):
    batches = Batch.objects.all()
    cattles = Cattle.objects.all()
    today = date.today()

    if request.method == 'POST':
        batch = Batch.objects.get(id=request.POST.get('batch'))
        cattle = Cattle.objects.get(id=request.POST.get('cattle'))
        feed_type = request.POST.get('feed_type')
        quantity = float(request.POST.get('quantity'))
        unit = request.POST.get('unit')
        feed_date = request.POST.get('feed_date')
        notes = request.POST.get('notes')

        FeedStock.objects.create(
            batch=batch,
            cattle=cattle,
            feed_type=feed_type,
            quantity=quantity,
            unit=unit,
            feed_date=feed_date,
            notes=notes
        )
        return redirect('feed_list')

    return render(request, 'feed/add_feed.html', {'batches': batches, 'cattles': cattles, 'today': today})


# Breed List
def feed_list(request):
    records = FeedStock.objects.all().order_by('-feed_date')
    return render(request, 'feed/feed_list.html', {'records': records})


# Add Income
def add_income(request):
    batches = Batch.objects.all()
    cattles = Cattle.objects.all()
    today = date.today()

    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        source = request.POST.get('source')
        batch_id = request.POST.get('batch')
        cattle_id = request.POST.get('cattle')
        income_date = request.POST.get('income_date')
        notes = request.POST.get('notes')

        batch = Batch.objects.get(id=batch_id) if batch_id else None
        cattle = Cattle.objects.get(id=cattle_id) if cattle_id else None

        Income.objects.create(
            amount=amount,
            source=source,
            batch=batch,
            cattle=cattle,
            income_date=income_date,
            notes=notes
        )
        return redirect('income_list')

    return render(request, 'income/add_income.html', {'batches': batches, 'cattles': cattles, 'today': today})


# Income List
def income_list(request):
    records = Income.objects.all().order_by('-income_date')
    total_income = sum([rec.amount for rec in records])
    return render(request, 'income/income_list.html', {'records': records, 'total_income': total_income})


# Reports
def report(request):
    cattles = Cattle.objects.all()
    report_data = []

    for cattle in cattles:
        batch = cattle.batch
        # Latest health record
        latest_health = cattle.health_records.order_by('-vaccination_date').first()
        # Total feed quantity
        total_feed = sum([f.quantity for f in cattle.feed_records.all()])
        # Total income for this cattle
        total_income = sum([i.amount for i in cattle.income_records.all()])
        # Total milk produced
        total_milk = sum([m.amount for m in cattle.milkings.all()])
        # Latest milking info
        latest_milking = cattle.milkings.order_by('-date').first()

        report_data.append({
            'cattle': cattle,
            'batch': batch,
            'health': latest_health,
            'total_feed': total_feed,
            'total_income': total_income,
            'total_milk': total_milk,
            'latest_milking': latest_milking,
        })

    return render(request, 'report/report.html', {'report_data': report_data})




def alert(request):
    today = date.today()

    # 1️⃣ Missed / expired convincing dates
    missed_convincing = Cattle.objects.filter(
        convincing_date__lte=today
    ).exclude(convincing_date=None).order_by('convincing_date')

    # 2️⃣ Near expiry convincing dates (next 3 days)
    near_expiry_convincing = Cattle.objects.filter(
        convincing_date__gt=today,
        convincing_date__lte=today + timedelta(days=3)
    ).order_by('convincing_date')
    
    context = {
        'missed_convincing': missed_convincing,
        'near_expiry_convincing': near_expiry_convincing,

    }
    return render(request,'alert.html',context)



def update_cattle(request, id):
    cattle = Cattle.objects.get(id=id)
    batches = Batch.objects.all()

    if request.method == "POST":

        # Safe update function
        def get_value(key):
            value = request.POST.get(key)
            return value if value not in ("", None) else None
        
        cattle.batch_id = get_value('batch')
        cattle.name = get_value('name')
        cattle.age = get_value('age')
        cattle.breed = get_value('breed')
        cattle.milk = get_value('milk')
        cattle.purchase = get_value('purchase')
        cattle.purchase_amount = get_value('purchase_amount')
        cattle.breeding = get_value('breeding')
        cattle.health_status = get_value('health_status')
        cattle.convincing_date = get_value('convincing_date')
        cattle.result = get_value('result')

        cattle.milk_day_15 = get_value('milk_day_15')
        cattle.milk_day_30 = get_value('milk_day_30')
        cattle.milk_day_60 = get_value('milk_day_60')
        cattle.milk_day_75 = get_value('milk_day_75')

        cattle.outward_date = get_value('outward_date')

        cattle.save()
        return redirect('cattle_list')

    breeds = ["Murrah", "Jaffarabadi", "Surti", "Mehsana", "Nili-Ravi", "Bhadawari", "Pandharpuri"]
    breeding_states = ["Fresh", "Inseminated", "Pregnant", "Dry"]

    return render(request, 'cattle/update_cattle.html', {
        'cattle': cattle,
        'batches': batches,
        'breeds': breeds,
        'breeding_states': breeding_states
    })
