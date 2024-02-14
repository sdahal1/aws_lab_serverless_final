// GptChat.js
import React, { useState } from 'react';
import axios from 'axios';

const GptChat = () => {
  const [input, setInput] = useState();
  const [output, setOutput] = useState('');
  const api_key = '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';
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${api_key}`
  };
  const api_endpoint_url = "https://api.openai.com/v1/chat/completions"

  const handleAskQuestion = async () => {
    const prompt = 'Tell me the following in a funny way sounding like you are a comedian with metaphors.';
    try {
      const response = await axios.post(api_endpoint_url, { model: "gpt-3.5-turbo", prompt: `${prompt} ${input}`}, {headers});
      console.log('Response:', response.data);
      setOutput(response.data.answer); // Adjust based on your API response structure
    } catch (error) {
      console.error('Error asking question:', error);
    }
  };

  

  return (
    <div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleAskQuestion}>Ask</button>
      {output && <p>{output}</p>}
    </div>
  );
};

export default GptChat;
