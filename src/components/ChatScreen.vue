<template>
    <div class="chat-screen">
      <div v-for="(msg, i) in messages" :key="i" class="chat-message">
        <b>{{ msg.role }}:</b> {{ msg.content }}
      </div>
      <form @submit.prevent="sendMessage">
        <input v-model="input" placeholder="Ask something about the flight…" />
        <button type="submit">Send</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    props: ['sessionId'],
    data() {
      return {
        input: '',
        messages: []
      }
    },
    methods: {
      async sendMessage() {
        const userMsg = { role: 'user', content: this.input };
        this.messages.push(userMsg);
        this.input = '';
  
        const res = await fetch(`/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: this.sessionId,
            message: userMsg.content
          })
        });
        const data = await res.json();
        this.messages.push({ role: 'assistant', content: data.response });
      }
    }
  }
  </script>
  
  <style scoped>
  .chat-screen {
    padding: 1rem;
    background: #f9f9f9;
  }
  .chat-message {
    margin-bottom: 0.5rem;
  }
  input {
    width: 80%;
    margin-right: 0.5rem;
  }
  </style>
  