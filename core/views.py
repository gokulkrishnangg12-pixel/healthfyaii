from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, ImageUpload, ScanResult, IngredientLog, ProductAlternative
from .ocr import process_image_with_ocr, process_expiry_image
from .ai_model import classify_ingredients, apply_personalization, analyze_levels
from .recommendations import get_healthier_alternatives
import datetime
import calendar

def get_or_create_dummy_profile():
    # For demo purposes, fetch the first profile or create a default one
    profile, created = UserProfile.objects.get_or_create(id=1, defaults={'name': 'Demo User'})
    return profile

def index(request):
    if request.method == 'POST' and request.FILES.get('expiry_image'):
        image = request.FILES['expiry_image']
        profile = get_or_create_dummy_profile()
        
        # Save expiry image
        upload = ImageUpload.objects.create(user=profile, expiry_image=image)
        
        return redirect('scan_ingredients', upload_id=upload.id)
        
    return render(request, 'index.html')

def scan_ingredients(request, upload_id):
    upload = get_object_or_404(ImageUpload, id=upload_id)
    if request.method == 'POST' and request.FILES.get('label_image'):
        image = request.FILES['label_image']
        upload.image = image
        upload.save()
        profile = get_or_create_dummy_profile()
        
        # Step 1: OCR on Expiry Date
        expiry_data = {"expiry_date": None, "is_expired": False}
        if upload.expiry_image:
            extracted_data = process_expiry_image(upload.expiry_image.path)
            
            # Logic to calculate expiry against scan date
            scan_date = datetime.date.today()
            calc_expiry_date = None
            is_expired = False
            
            if extracted_data.get('extracted_mfg_date') and extracted_data.get('extracted_best_before_months'):
                try:
                    # Parsing format YYYY-MM-DD
                    mfg_date = datetime.datetime.strptime(extracted_data['extracted_mfg_date'], "%Y-%m-%d").date()
                    months = int(extracted_data['extracted_best_before_months'])
                    
                    # Add months to mfg_date
                    new_month = mfg_date.month - 1 + months
                    year = mfg_date.year + new_month // 12
                    new_month = new_month % 12 + 1
                    day = min(mfg_date.day, calendar.monthrange(year, new_month)[1])
                    calc_expiry_date = datetime.date(year, new_month, day)
                    
                    is_expired = calc_expiry_date < scan_date
                    expiry_data["expiry_date"] = calc_expiry_date.strftime("%B %d, %Y")
                except ValueError:
                    pass
            elif extracted_data.get('extracted_expiry_date'):
                try:
                    calc_expiry_date = datetime.datetime.strptime(extracted_data['extracted_expiry_date'], "%Y-%m-%d").date()
                    is_expired = calc_expiry_date < scan_date
                    expiry_data["expiry_date"] = calc_expiry_date.strftime("%B %d, %Y")
                except ValueError:
                    expiry_data["expiry_date"] = extracted_data['extracted_expiry_date']
            
            expiry_data["is_expired"] = is_expired
        
        # Step 2: OCR on Ingredients
        ocr_data = process_image_with_ocr(upload.image.path)
        
        # Step 3: AI Classification
        base_analysis = classify_ingredients(ocr_data['ingredients'])
        
        # Step 4: Personalization
        final_analysis = apply_personalization(base_analysis, profile)
        
        # Step 4.5: Analyze specific breakdown levels
        nutrition_levels = analyze_levels(ocr_data.get('ingredients', []), ocr_data.get('nutrition', {}))
        
        # Save Scan Result
        scan_result = ScanResult.objects.create(
            image_upload=upload,
            health_score=final_analysis['health_score'],
            grade=final_analysis['grade'],
            warnings=final_analysis['warnings'],
            nutrition_levels=nutrition_levels,
            expiry_date=expiry_data.get('expiry_date'),
            is_expired=expiry_data.get('is_expired', False)
        )
        
        # Save Logs
        for log in final_analysis['ingredient_logs']:
            IngredientLog.objects.create(
                scan_result=scan_result,
                ingredient_name=log['ingredient_name'],
                risk_level=log['risk_level'],
                description=log['description']
            )
            
        # Step 5: Alternatives
        alternatives = get_healthier_alternatives(final_analysis['warnings'])
        for alt in alternatives:
            ProductAlternative.objects.create(
                scan_result=scan_result,
                suggestion_name=alt['suggestion_name'],
                reason=alt['reason'],
                image_url=alt['image_url']
            )
            
        return redirect('result', scan_id=scan_result.id)
        
    return render(request, 'scan_ingredients.html', {'upload': upload})

def profile(request):
    user_profile = get_or_create_dummy_profile()
    
    if request.method == 'POST':
        user_profile.name = request.POST.get('name', user_profile.name)
        user_profile.diabetes = request.POST.get('diabetes') == 'on'
        user_profile.hypertension = request.POST.get('hypertension') == 'on'
        user_profile.vegan = request.POST.get('vegan') == 'on'
        user_profile.save()
        return redirect('index')
        
    return render(request, 'profile.html', {'profile': user_profile})

def result(request, scan_id):
    scan_result = get_object_or_404(ScanResult, id=scan_id)
    return render(request, 'result.html', {'result': scan_result})
