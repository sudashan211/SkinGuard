/**
 * Sync Service
 * Requirements: 21.3, 21.4
 * 
 * Handles offline data storage and synchronization when network is restored
 */

interface PendingUpload {
  id: string;
  type: 'image_analysis' | 'appointment' | 'profile_update';
  data: any;
  timestamp: number;
  retryCount: number;
}

const PENDING_UPLOADS_KEY = 'skinguard_pending_uploads';
const MAX_RETRY_COUNT = 3;

class SyncService {
  /**
   * Add an upload to the pending queue
   */
  addPendingUpload(type: PendingUpload['type'], data: any): string {
    const uploads = this.getPendingUploads();
    const id = `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const upload: PendingUpload = {
      id,
      type,
      data,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    uploads.push(upload);
    this.savePendingUploads(uploads);
    
    console.log(`Added pending upload: ${id}`);
    return id;
  }

  /**
   * Get all pending uploads
   */
  getPendingUploads(): PendingUpload[] {
    try {
      const stored = localStorage.getItem(PENDING_UPLOADS_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error reading pending uploads:', error);
      return [];
    }
  }

  /**
   * Save pending uploads to localStorage
   */
  private savePendingUploads(uploads: PendingUpload[]): void {
    try {
      localStorage.setItem(PENDING_UPLOADS_KEY, JSON.stringify(uploads));
    } catch (error) {
      console.error('Error saving pending uploads:', error);
    }
  }

  /**
   * Remove a pending upload
   */
  removePendingUpload(id: string): void {
    const uploads = this.getPendingUploads();
    const filtered = uploads.filter(u => u.id !== id);
    this.savePendingUploads(filtered);
    console.log(`Removed pending upload: ${id}`);
  }

  /**
   * Sync all pending uploads
   */
  async syncPendingUploads(): Promise<{ success: number; failed: number }> {
    const uploads = this.getPendingUploads();
    
    if (uploads.length === 0) {
      console.log('No pending uploads to sync');
      return { success: 0, failed: 0 };
    }

    console.log(`Syncing ${uploads.length} pending uploads...`);
    
    let successCount = 0;
    let failedCount = 0;

    for (const upload of uploads) {
      try {
        await this.syncUpload(upload);
        this.removePendingUpload(upload.id);
        successCount++;
      } catch (error) {
        console.error(`Failed to sync upload ${upload.id}:`, error);
        
        // Increment retry count
        upload.retryCount++;
        
        if (upload.retryCount >= MAX_RETRY_COUNT) {
          console.error(`Max retries reached for upload ${upload.id}, removing from queue`);
          this.removePendingUpload(upload.id);
        } else {
          // Update retry count
          const uploads = this.getPendingUploads();
          const index = uploads.findIndex(u => u.id === upload.id);
          if (index !== -1) {
            uploads[index] = upload;
            this.savePendingUploads(uploads);
          }
        }
        
        failedCount++;
      }
    }

    console.log(`Sync complete: ${successCount} success, ${failedCount} failed`);
    return { success: successCount, failed: failedCount };
  }

  /**
   * Sync a single upload
   */
  private async syncUpload(upload: PendingUpload): Promise<void> {
    switch (upload.type) {
      case 'image_analysis':
        await this.syncImageAnalysis(upload.data);
        break;
      case 'appointment':
        await this.syncAppointment(upload.data);
        break;
      case 'profile_update':
        await this.syncProfileUpdate(upload.data);
        break;
      default:
        throw new Error(`Unknown upload type: ${upload.type}`);
    }
  }

  /**
   * Sync image analysis upload
   */
  private async syncImageAnalysis(data: any): Promise<void> {
    const formData = new FormData();
    formData.append('image', data.image);
    if (data.symptoms) {
      formData.append('symptoms', JSON.stringify(data.symptoms));
    }

    const response = await fetch('/api/analyze-skin', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    if (!response.ok) {
      throw new Error(`Image analysis sync failed: ${response.statusText}`);
    }
  }

  /**
   * Sync appointment booking
   */
  private async syncAppointment(data: any): Promise<void> {
    const response = await fetch('/api/appointments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Appointment sync failed: ${response.statusText}`);
    }
  }

  /**
   * Sync profile update
   */
  private async syncProfileUpdate(data: any): Promise<void> {
    const response = await fetch('/api/patient/profile', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Profile update sync failed: ${response.statusText}`);
    }
  }

  /**
   * Clear all pending uploads (use with caution)
   */
  clearAllPendingUploads(): void {
    localStorage.removeItem(PENDING_UPLOADS_KEY);
    console.log('Cleared all pending uploads');
  }

  /**
   * Get pending upload count
   */
  getPendingUploadCount(): number {
    return this.getPendingUploads().length;
  }
}

export const syncService = new SyncService();
