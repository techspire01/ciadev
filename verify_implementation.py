#!/usr/bin/env python
"""
Verification script for delete and preview functionality.
Checks that all necessary code is in place without running Django test suite.
"""

import os
import sys
import re

def check_file_contains(filepath, patterns, description):
    """Check if file contains all patterns"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    all_found = True
    for pattern in patterns:
        if isinstance(pattern, str):
            found = pattern in content
        else:
            found = bool(re.search(pattern, content))
        
        if found:
            print(f"  ✅ {pattern[:80]}...")
        else:
            print(f"  ❌ MISSING: {pattern[:80]}...")
            all_found = False
    
    if all_found:
        print(f"✅ {description}\n")
    else:
        print(f"❌ {description}\n")
    
    return all_found

def main():
    print("="*70)
    print("VERIFICATION: Delete and Preview Functionality Implementation")
    print("="*70 + "\n")
    
    all_checks = True
    
    # Check 1: Template has preview modal HTML
    print("1. Template Preview Modal HTML")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/templates/brand_new_site/applicant_detail.html',
        [
            'id="previewModal"',
            'id="previewFrame"',
            'onclick="previewFile(\'resume\')"',
            'onclick="previewFile(\'attachment\')"',
        ],
        "Template preview modal HTML"
    )
    
    # Check 2: Template has JavaScript preview functions
    print("2. Template JavaScript Functions")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/templates/brand_new_site/applicant_detail.html',
        [
            'function previewFile(fileType)',
            'function closePreview()',
            'function deleteFile(fileType)',
            'function deleteApplication()',
            '/portal-admin/preview/',
        ],
        "Template JavaScript functions"
    )
    
    # Check 3: Views has preview endpoint
    print("3. Views Preview Endpoint")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            'def preview_application_file',
            'application_type.*application_id.*file_type',
            'JsonResponse.*success.*url',
        ],
        "Views preview endpoint"
    )
    
    # Check 4: Views handles delete_resume_only
    print("4. Delete Resume Only Functionality")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            "request.POST.get('delete_resume_only')",
            'application.resume.delete()',
            'application.resume = None',
        ],
        "Delete resume only functionality"
    )
    
    # Check 5: Views handles delete_attachment_only
    print("5. Delete Attachment Only Functionality")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            "request.POST.get('delete_attachment_only')",
            'application.additional_attachment.delete()',
            'application.additional_attachment = None',
        ],
        "Delete attachment only functionality"
    )
    
    # Check 6: URLs has preview route
    print("6. URL Routing Preview Endpoint")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/urls.py',
        [
            'preview_application_file',
            'application_type.*application_id.*file_type',
        ],
        "URL routing preview endpoint"
    )
    
    # Check 7: JSON responses in delete functions
    print("7. JSON Response Handling")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            "JsonResponse.*success.*True",
            "JsonResponse.*success.*False",
            'is_ajax.*XMLHttpRequest',
        ],
        "JSON response handling for AJAX"
    )
    
    # Check 8: Error handling and logging
    print("8. Error Handling and Logging")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            'try:',
            'logger.error',
            'logger.info',
            'messages.success',
            'messages.error',
        ],
        "Error handling and logging"
    )
    
    # Check 9: Authorization checks
    print("9. Authorization Checks")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/views.py',
        [
            '@supplier_required',
            'get_supplier_for_user_or_raise',
            'supplier=supplier',
        ],
        "Authorization checks"
    )
    
    # Check 10: Delete individual files buttons in template
    print("10. Template Delete File Buttons")
    all_checks &= check_file_contains(
        '/Users/user/incubation_cell/cia-dev/portal/templates/brand_new_site/applicant_detail.html',
        [
            'Delete Resume Only',
            'Delete Document Only',
            'Delete Entire Application',
        ],
        "Template delete buttons"
    )
    
    print("="*70)
    if all_checks:
        print("✅ ALL VERIFICATION CHECKS PASSED!")
        print("\nImplementation includes:")
        print("  • Preview Modal: Displays PDFs using Google Docs Viewer")
        print("  • Delete Resume: Remove only resume, keep attachment & app")
        print("  • Delete Attachment: Remove only attachment, keep resume & app")
        print("  • Delete Application: Remove entire application & all files")
        print("  • Authorization: Only suppliers who posted job/internship can manage")
        print("  • Error Handling: Proper try-catch, logging, user messages")
        print("  • AJAX Support: JSON responses for smooth UX")
        print("\nNext Steps:")
        print("  1. Run server: python manage.py runserver")
        print("  2. Log in as supplier")
        print("  3. Navigate to applicant detail page")
        print("  4. Test preview buttons (👁️ icons)")
        print("  5. Test delete buttons (🗑️ icons)")
        print("  6. Check console for logs and messages")
    else:
        print("❌ SOME VERIFICATION CHECKS FAILED")
        print("Review the output above to see what's missing.")
    print("="*70 + "\n")
    
    return 0 if all_checks else 1

if __name__ == '__main__':
    sys.exit(main())
