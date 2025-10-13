import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const question = formData.get('question') as string;
    const screenshot = formData.get('screenshot') as File | null;

    // Forward to Queen AI backend for Gemini Vision analysis
    const queenApiUrl = process.env.NEXT_PUBLIC_QUEEN_API_URL || 'http://localhost:8001';
    
    // Create form data for Queen AI
    const queenFormData = new FormData();
    queenFormData.append('question', question);
    queenFormData.append('context', 'metamask_setup'); // Context for Teacher Bee
    
    if (screenshot) {
      // Convert screenshot to base64 for Gemini Vision
      const bytes = await screenshot.arrayBuffer();
      const buffer = Buffer.from(bytes);
      const base64 = buffer.toString('base64');
      
      queenFormData.append('image', base64);
      queenFormData.append('image_type', screenshot.type);
    }

    // Call Queen AI backend
    const response = await fetch(`${queenApiUrl}/api/v1/teacher-bee/analyze-image`, {
      method: 'POST',
      body: queenFormData,
    });

    if (!response.ok) {
      throw new Error('Failed to analyze screenshot');
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      response: data.response || data.message
    });

  } catch (error) {
    console.error('[Teacher Bee Screenshot Analysis Error]', error);
    
    // Fallback response if Gemini/Queen AI unavailable
    const question = (await request.formData()).get('question') as string;
    
    let fallbackResponse = "I can see you're working on setting up MetaMask! 🦊\n\n";
    
    if (question.includes('Step 1') || question.toLowerCase().includes('install')) {
      fallbackResponse += "**Installing MetaMask:**\n";
      fallbackResponse += "1. Make sure you're on metamask.io/download\n";
      fallbackResponse += "2. Click the button for your browser\n";
      fallbackResponse += "3. You should see 'Add to Chrome' (or your browser)\n";
      fallbackResponse += "4. After installing, look for the 🦊 fox icon in your toolbar!\n\n";
      fallbackResponse += "Can you see the fox icon? If not, try refreshing your browser.";
    } else if (question.includes('Step 2') || question.toLowerCase().includes('create')) {
      fallbackResponse += "**Creating Your Wallet:**\n";
      fallbackResponse += "1. Click the 🦊 MetaMask icon\n";
      fallbackResponse += "2. You should see 'Create a new wallet' - click it\n";
      fallbackResponse += "3. Set a strong password (write it down!)\n";
      fallbackResponse += "4. Click 'Create'\n\n";
      fallbackResponse += "What step are you on? Describe what you see on screen.";
    } else if (question.includes('Step 3') || question.toLowerCase().includes('recovery') || question.toLowerCase().includes('phrase')) {
      fallbackResponse += "**Saving Recovery Phrase:**\n";
      fallbackResponse += "⚠️ This is the MOST important step!\n\n";
      fallbackResponse += "1. Click 'Reveal Secret Recovery Phrase'\n";
      fallbackResponse += "2. Write down ALL 12 words on paper (in order!)\n";
      fallbackResponse += "3. Never screenshot or type them on your computer\n";
      fallbackResponse += "4. Store the paper somewhere safe\n\n";
      fallbackResponse += "Have you written them down? Don't proceed without doing this!";
    } else {
      fallbackResponse += "I'm here to help you through MetaMask setup!\n\n";
      fallbackResponse += "Can you describe:\n";
      fallbackResponse += "• What step you're on (1-5)?\n";
      fallbackResponse += "• What you see on your screen?\n";
      fallbackResponse += "• What error message (if any)?\n\n";
      fallbackResponse += "I'll guide you through it step by step! 🐝";
    }

    return NextResponse.json({
      success: true,
      response: fallbackResponse,
      fallback: true
    });
  }
}
