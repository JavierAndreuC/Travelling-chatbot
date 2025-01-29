import { useState, useRef, useEffect } from "react";
import { ArrowUp, Loader2, Sparkles, User } from "lucide-react";

const Chat = () => {
  const [query, setQuery] = useState(""); // Store current user query
  const [loading, setLoading] = useState(false); // Manage state of the query
  const [messages, setMessages] = useState([]); // Store conversation messages to display in the chat
  const textareaRef = useRef(null); // Reference for the input text area
  const chatContainerRef = useRef(null); // Ref for chat container

  // Adjust height of the input text area based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  // Update on query value change
  useEffect(() => {
    adjustTextareaHeight();
  }, [query]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Function to manage the communication between the front and backend
  const handleSend = async () => {
    // Don't send empty query
    if (!query.trim()) return;

    // Store the current query and clear the input field
    const newQuery = query;
    setQuery("");

    // Add new message to the chat history
    setMessages((prev) => [...prev, { type: "user", content: newQuery }]);

    // Set state to loading while answer request is being processed
    setLoading(true);

    try {
      // Send query to backend "chat" Django view
      const res = await fetch("http://127.0.0.1:8000/chatbot/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          query: newQuery,
        }),
      });

      if (res.ok) {
        const data = await res.json(); // Parse the JSON response

        if (data.response) {
          // Add the bot's response to the chat if it has a valid response
          setMessages((prev) => [
            ...prev,
            { type: "bot", content: data.response },
          ]);
        } else {
          // Handle cases where the response format is incorrect
          setMessages((prev) => [
            ...prev,
            {
              type: "bot",
              content: "Error: No response field in API response.",
            },
          ]);
        }
      } else {
        // Handle errors when the request fails (e.g., server error)
        const errorDetails = await res.text();
        setMessages((prev) => [
          ...prev,
          {
            type: "bot",
            content: `Error: Unable to fetch response. Details: ${errorDetails}`,
          },
        ]);
      }
    } catch (error) {
      // Handle network or unexpected errors
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: `Error: Something went wrong: ${error.message}`,
        },
      ]);
    }

    // Set state back to normal after request recieved
    setLoading(false);
  };

  // Send message if Enter key is pressed
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Format and stylise response for better display
  const formatMessageContent = (content) => {
    // Process headers first
    const withHeaders = content
      .split("\n")
      .map((line) => {
        const headerMatch = line.match(/^###\s*(.+)/);
        if (headerMatch) {
          return `<span class="text-xl font-bold">${headerMatch[1]}</span>`;
        }
        return line;
      })
      .join("\n");

    // Then process rest of formatting
    return withHeaders
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br />")
      .replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s]+)\)/g,
        '<span>[</span><a href="$2" target="_blank" class="underline">$1</a><span>]</span>'
      );
  };

  return (
    <div className="flex flex-col items-center w-screen h-screen py-5 bg-zinc-900">
      <div className="w-full px-5 text-2xl font-bold text-white mb-6">
        Tomorrowland AI assistant
      </div>

      {/* Chat Wrapper */}
      <div
        ref={chatContainerRef}
        className="min-w-full h-full mb-4 rounded-lg text-white px-40 overflow-y-auto"
      >
        {/* Map messages to chat bubbles */}
        <div className="flex flex-col space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat ${
                message.type === "user" ? "chat-end" : "chat-start"
              }`}
            >
              {/* Speaker icon for the chat bubble */}
              <div className="chat-image">
                <div
                  className={`flex flex-row w-10 h-10 rounded-full items-center justify-center 
                  ${
                    message.type === "user" ? "bg-blue-400 overflow-clip" : ""
                  } `}
                >
                  {message.type === "user" ? (
                    <User size={38} className="mt-1" />
                  ) : (
                    <Sparkles size={38} className="mt-3" />
                  )}
                </div>
              </div>
              {/* Chat bubble with message */}
              <div
                className={`chat-bubble ${
                  message.type === "user"
                    ? "bg-zinc-500 text-white"
                    : "bg-amber-600 text-black font-medium text-left leading-relaxed p-4"
                }`}
                dangerouslySetInnerHTML={{
                  __html: formatMessageContent(message.content),
                }}
              ></div>
            </div>
          ))}
          {/* Temporary chat bubble while message loads */}
          {loading && (
            <div className="chat chat-start">
              <div className="chat-image">
                <div className="flex flex-row w-10 h-10 rounded-full items-center justify-center">
                  <Sparkles size={38} className="mt-3" />
                </div>
              </div>
              <div className="chat-bubble bg-amber-600 text-black font-medium">
                <Loader2 className="animate-spin" />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Prompt input box */}
      <div className="w-full h-fit px-40">
        <div className="flex flex-row w-full bg-zinc-700 rounded-3xl py-1 pl-7 pr-5 items-center">
          {/* Input area */}
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about Tomorrowland..."
            className="w-full min-h-12 max-h-52 border-0 align-text-bottom bg-transparent text-white placeholder-zinc-400 focus:outline-none resize-none overflow-y-auto"
            style={{ lineHeight: "20px", padding: "6px 0" }}
          ></textarea>
          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={loading}
            className={`btn btn-circle p-2 border-none bg-gray-50 text-black hover:bg-gray-200 flex-shrink-0 ${
              loading ? "cursor-not-allowed opacity-50" : "cursor-pointer"
            }`}
          >
            {loading ? (
              <Loader2 strokeWidth={3} className="animate-spin" />
            ) : (
              <ArrowUp strokeWidth={3} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
