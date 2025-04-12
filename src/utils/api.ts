export async function uploadSessionData(
  videoBlob: Blob | null,
  conversationData: any,
  sessionId: string | null
) {
  try {
    const formData = new FormData();
    
    // Add session ID
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    
    // Add video file if exists
    if (videoBlob) {
      const timestamp = new Date().getTime();
      formData.append('video', videoBlob, `session_${timestamp}_video.webm`);
    }
    
    // Add conversation data
    formData.append('conversation', JSON.stringify(conversationData));

    // Send to your backend (note the different port)
    const response = await fetch('http://localhost:9084/save-session', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload session data');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading session data:', error);
    throw error;
  }
} 