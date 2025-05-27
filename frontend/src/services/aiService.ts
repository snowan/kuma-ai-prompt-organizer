interface AISuggestionResponse {
  improved_prompt: string;
  suggestions: string[];
  tags: string[];
}

export const getAIPromptSuggestions = async (
  prompt: string,
  apiKey?: string
): Promise<AISuggestionResponse> => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/ai/suggestions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
      },
      body: JSON.stringify({ prompt })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to get AI suggestions');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting AI suggestions:', error);
    throw error;
  }
};
