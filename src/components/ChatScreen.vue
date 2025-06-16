<template>
    <div class="chat-screen">
      <h3>Chat With Your Flight Log</h3>
      <div v-for="msg in messages" :key="msg.id" class="message">
        <p><strong>{{ msg.role }}:</strong> {{ msg.content }}</p>
      </div>
      <input
        v-model="userMessage"
        @keyup.enter="sendMessage"
        placeholder="Ask something..."
      />
    </div>
  </template>
  
  <script>
  export default {
    props: ['sessionId'],
    data() {
      return {
        userMessage: '',
        messages: []
      };
    },
    methods: {
      async sendMessage() {
        if (!this.userMessage) return;
  
        const body = {
          session_id: this.sessionId,
          message: this.userMessage
        };
  
        try {
          const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
          });
  
          const result = await res.json();
  
          this.messages.push({ role: 'You', content: this.userMessage });
          this.messages.push({ role: 'AI', content: result.response });
  
          this.userMessage = '';
        } catch (err) {
          console.error('Chat error:', err);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .chat-screen {
    padding: 1rem;
    background: #f8f8f8;
    border: 1px solid #ddd;
  }
  
  .message {
    margin-bottom: 10px;
  }
  
  input {
    width: 100%;
    padding: 8px;
  }
  </style>
  