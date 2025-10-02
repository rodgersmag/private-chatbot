# Ollama Chat UI# React + TypeScript + Vite



A modern, responsive chat interface for Ollama built with React, Vite, and Tailwind CSS v4. Features real-time streaming responses, conversation management, and a beautiful ChatGPT-inspired design.This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.



## ✨ FeaturesCurrently, two official plugins are available:



- 💬 **Real-time Streaming**: Watch AI responses appear token by token- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh

- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

- 🎨 **Modern UI**: Clean, ChatGPT-inspired interface with light/dark themes

- 💾 **Persistent Storage**: Conversations saved locally in browser## React Compiler

- ⚙️ **Customizable Settings**: Adjust model, temperature, and system prompts

- 🔄 **Multiple Conversations**: Create and manage multiple chat sessionsThe React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

- 📝 **Markdown Support**: Rich formatting with code syntax highlighting

- ⌨️ **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line## Expanding the ESLint configuration



## 🚀 Quick StartIf you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:



### Development```js

export default defineConfig([

```bash  globalIgnores(['dist']),

# Install dependencies  {

npm install    files: ['**/*.{ts,tsx}'],

    extends: [

# Start development server      // Other configs...

npm run dev

      // Remove tseslint.configs.recommended and replace with this

# Open http://localhost:5173      tseslint.configs.recommendedTypeChecked,

```      // Alternatively, use this for stricter rules

      tseslint.configs.strictTypeChecked,

### Production      // Optionally, add this for stylistic rules

      tseslint.configs.stylisticTypeChecked,

```bash

# Build for production      // Other configs...

npm run build    ],

    languageOptions: {

# Preview production build      parserOptions: {

npm run preview        project: ['./tsconfig.node.json', './tsconfig.app.json'],

```        tsconfigRootDir: import.meta.dirname,

      },

### Docker      // other options...

    },

```bash  },

# From parent directory])

docker-compose up -d```



# Access at http://localhost:3000You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```

```js

## 🛠️ Tech Stack// eslint.config.js

import reactX from 'eslint-plugin-react-x'

- **Frontend**: React 19 + TypeScriptimport reactDom from 'eslint-plugin-react-dom'

- **Build Tool**: Vite 7  

- **Styling**: Tailwind CSS v4export default defineConfig([

- **State**: Zustand + React Query  globalIgnores(['dist']),

- **Markdown**: react-markdown + rehype-highlight  {

- **Icons**: Lucide React    files: ['**/*.{ts,tsx}'],

    extends: [

## 📁 Project Structure      // Other configs...

      // Enable lint rules for React

```      reactX.configs['recommended-typescript'],

src/      // Enable lint rules for React DOM

├── components/          # React components      reactDom.configs.recommended,

│   ├── ChatPanel.tsx    # Main chat interface    ],

│   ├── Composer.tsx     # Message input    languageOptions: {

│   ├── Message.tsx      # Message display      parserOptions: {

│   ├── Sidebar.tsx      # Conversation list        project: ['./tsconfig.node.json', './tsconfig.app.json'],

│   └── SettingsModal.tsx # Settings        tsconfigRootDir: import.meta.dirname,

├── lib/api.ts           # Ollama API client      },

├── store/chat.ts        # Zustand store      // other options...

├── types.ts             # TypeScript types    },

└── App.tsx              # Root component  },

```])

```

## ⚙️ Configuration

Create `.env`:

```env
VITE_OLLAMA_URL=/ollama
VITE_DEFAULT_MODEL=qwen3:1.7b
```

## 🎯 Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line
- `Esc` - Close modals

## 🔧 Troubleshooting

**CORS Issues**: Vite proxy handles this in development. For production, use the Nginx configuration provided.

**Connection Failed**: Verify Ollama is running with `ollama list`

**Build Errors**: Delete `node_modules` and reinstall dependencies

## 📝 License

MIT License

---

Built with ❤️ for the Ollama community
