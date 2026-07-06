-- SkinGuard Storage Bucket Configuration
-- Migration 003: Supabase Storage Setup
-- Requirements: 12.1, 12.3

-- ============================================================================
-- STORAGE BUCKETS
-- Note: Storage buckets are typically created via Supabase Dashboard or API
-- This file documents the required configuration
-- ============================================================================

-- Create storage bucket for medical images
-- Bucket name: medical-images
-- Configuration:
--   - Public: false (private bucket)
--   - File size limit: 10MB
--   - Allowed MIME types: image/jpeg, image/png, image/jpg
--   - Encryption: AES-256 (enabled by default in Supabase)

-- SQL equivalent (if using Supabase SQL):
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'medical-images',
    'medical-images',
    false,
    10485760, -- 10MB in bytes
    ARRAY['image/jpeg', 'image/png', 'image/jpg']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STORAGE POLICIES
-- Control access to medical images
-- ============================================================================

-- Patients can upload images to their own folder
CREATE POLICY "Patients can upload own images"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'medical-images'
        AND auth.uid()::text = (storage.foldername(name))[1]
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'patient'
        )
    );

-- Patients can view their own images
CREATE POLICY "Patients can view own images"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'medical-images'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Verified doctors can view images from reports they have access to
CREATE POLICY "Doctors can view patient images"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'medical-images'
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'doctor' AND verified = TRUE
        )
        AND EXISTS (
            SELECT 1 FROM medical_reports
            WHERE medical_reports.image_url LIKE '%' || name || '%'
            AND medical_reports.status IN ('safe', 'urgent')
        )
    );

-- Admins can view all images
CREATE POLICY "Admins can view all images"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'medical-images'
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can delete images (for content moderation)
CREATE POLICY "Admins can delete images"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'medical-images'
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Patients can delete their own images
CREATE POLICY "Patients can delete own images"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'medical-images'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================================================
-- STORAGE HELPER FUNCTIONS
-- ============================================================================

-- Function to generate storage path for patient images
CREATE OR REPLACE FUNCTION generate_image_path(patient_id UUID, filename TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN patient_id::text || '/' || gen_random_uuid()::text || '_' || filename;
END;
$$ LANGUAGE plpgsql;

-- Function to get signed URL for image (valid for 1 hour)
CREATE OR REPLACE FUNCTION get_signed_image_url(image_path TEXT)
RETURNS TEXT AS $$
DECLARE
    signed_url TEXT;
BEGIN
    -- This would typically be handled by the backend API using Supabase client
    -- Documented here for reference
    -- signed_url := storage.create_signed_url('medical-images', image_path, 3600);
    RETURN 'https://your-project.supabase.co/storage/v1/object/sign/medical-images/' || image_path;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STORAGE CLEANUP FUNCTIONS
-- ============================================================================

-- Function to delete orphaned images (images not referenced in medical_reports)
CREATE OR REPLACE FUNCTION cleanup_orphaned_images()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- This would typically be run as a scheduled job
    -- Identifies images in storage that don't have corresponding medical_reports entries
    
    -- Note: Actual deletion would be done via Supabase Storage API
    -- This function documents the logic
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to delete images for deleted accounts (after 30 day grace period)
CREATE OR REPLACE FUNCTION cleanup_deleted_account_images()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete images for accounts deleted more than 30 days ago
    -- This supports the account deletion requirement (18.3)
    
    -- Note: Actual deletion would be done via Supabase Storage API
    -- This function documents the logic
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
