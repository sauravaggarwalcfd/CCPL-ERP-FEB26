import { useState } from 'react'

export default function ImageUploadField({ onImageChange, currentImage }) {
  const [preview, setPreview] = useState(currentImage || null)
  const [uploading, setUploading] = useState(false)

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file size (1MB max as per requirement)
    if (file.size > 1 * 1024 * 1024) {
      alert('Image too large. Max 1MB (as per system requirements)')
      e.target.value = ''
      return
    }

    // Validate file type (JPEG and PNG only as per requirement)
    if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
      alert('Please select only JPEG or PNG images')
      e.target.value = ''
      return
    }

    // Create preview and convert to BASE64
    const reader = new FileReader()
    reader.onload = (event) => {
      const imageData = event.target.result
      setPreview(imageData)

      // Pass back the BASE64 data (without data:image/jpeg;base64, prefix for storage)
      const base64Data = imageData.split(',')[1]
      onImageChange(file, base64Data, file.type)
    }
    reader.readAsDataURL(file)
  }

  const handleRemove = () => {
    setPreview(null)
    onImageChange(null, null, null)
  }

  return (
    <div style={{
      marginBottom: '20px',
      padding: '15px',
      border: '2px solid #e0e0e0',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9'
    }}>
      <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', fontWeight: '600' }}>Item Image</h3>

      {preview ? (
        <>
          <div style={{
            width: '200px',
            height: '200px',
            borderRadius: '8px',
            overflow: 'hidden',
            marginBottom: '15px',
            border: '2px solid #ddd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <img
              src={preview}
              alt="Item preview"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <label style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              📷 Change Image
              <input
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleImageSelect}
                style={{ display: 'none' }}
              />
            </label>

            <button
              type="button"
              onClick={handleRemove}
              style={{
                padding: '10px 20px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              ✕ Remove Image
            </button>
          </div>
        </>
      ) : (
        <label style={{
          display: 'block',
          padding: '40px 20px',
          border: '2px dashed #007bff',
          borderRadius: '8px',
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: '#f0f7ff',
          transition: 'all 0.3s ease'
        }}>
          <p style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#333' }}>
            📸 Click to upload image
          </p>
          <p style={{ margin: '0', fontSize: '12px', color: '#666' }}>
            JPEG or PNG only (Max 1MB)
          </p>
          <input
            type="file"
            accept="image/jpeg,image/jpg,image/png"
            onChange={handleImageSelect}
            style={{ display: 'none' }}
          />
        </label>
      )}
    </div>
  )
}
