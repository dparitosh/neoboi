import React, { useState, useEffect, useRef, useCallback } from 'react';

const ChatInterface = ({ onGraphUpdate, loading: parentLoading }) => {
    const [chatMessages, setChatMessages] = useState([]);
    const [chatInputValue, setChatInputValue] = useState('');
    const [isChatSending, setIsChatSending] = useState(false);
    const chatMessagesRef = useRef(null);
    const [isUserAtBottom, setIsUserAtBottom] = useState(true);
    const [showScrollToBottom, setShowScrollToBottom] = useState(false);

    // Chat scrolling functions
    const scrollToBottom = useCallback(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
            setIsUserAtBottom(true);
            setShowScrollToBottom(false);
        }
    }, []);

    const handleChatScroll = useCallback(() => {
        if (chatMessagesRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
            const atBottom = scrollTop + clientHeight >= scrollHeight - 10; // 10px tolerance
            setIsUserAtBottom(atBottom);
            setShowScrollToBottom(!atBottom && chatMessages.length > 3); // Show button if scrolled up and has messages
        }
    }, [chatMessages.length]);

    // Auto-scroll to bottom when new messages are added
    useEffect(() => {
        if (isUserAtBottom && chatMessagesRef.current) {
            // Small delay to ensure DOM is updated
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        }
    }, [chatMessages, isUserAtBottom, scrollToBottom]);

    const handleRegularChat = async (userMessage) => {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userMessage })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Chat API error: ${response.status}`);
        }
        
        const llmResponse = await response.json();
        setChatMessages(prev => [...prev, { sender: 'AI', text: llmResponse.textResponse || "Received a response." }]);

        // If the response includes graph data, update the parent
        if (llmResponse.graphData && llmResponse.graphData.nodes && llmResponse.graphData.edges) {
            console.log("[ChatInterface] Received new graph data from chat:", llmResponse.graphData);
            if (onGraphUpdate) {
                onGraphUpdate(llmResponse.graphData);
            }
        }
    };

    // Chat Logic with dynamic graph updates
    const handleSendChatMessage = async () => {
        if (!chatInputValue.trim()) return;
        const userMessage = chatInputValue.trim();
        setChatMessages(prev => [...prev, { sender: 'You', text: userMessage }]);
        setChatInputValue('');
        setIsChatSending(true);
        
        try {
            // Check for specific commands
            if (userMessage.toLowerCase().includes('refresh') || userMessage.toLowerCase().includes('reload')) {
                // Refresh graph data
                const response = await fetch('/api/graph');
                if (response.ok) {
                    const data = await response.json();
                    if (onGraphUpdate) {
                        onGraphUpdate(data);
                    }
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Graph data refreshed successfully!' }]);
                } else {
                    throw new Error('Failed to refresh graph data');
                }
            } else if (userMessage.toLowerCase().includes('expand') || userMessage.toLowerCase().includes('more')) {
                // Try to get more nodes/relationships
                const response = await fetch('/api/graph/all');
                if (response.ok) {
                    const data = await response.json();
                    if (onGraphUpdate) {
                        onGraphUpdate(data);
                    }
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Showing expanded graph with more data!' }]);
                } else {
                    // Fallback to chat API
                    await handleRegularChat(userMessage);
                }
            } else if (userMessage.toLowerCase().includes('reset') || userMessage.toLowerCase().includes('show all')) {
                // Reset to original data
                const response = await fetch('/api/graph');
                if (response.ok) {
                    const data = await response.json();
                    if (onGraphUpdate) {
                        onGraphUpdate(data);
                    }
                    setChatMessages(prev => [...prev, { sender: 'AI', text: 'Reset to original graph data' }]);
                }
            } else {
                // Regular chat with potential graph updates
                await handleRegularChat(userMessage);
            }
        } catch (error) {
            console.error('Error sending message or processing response:', error);
            setChatMessages(prev => [...prev, { sender: 'System', text: `Error: ${error.message}` }]);
        } finally {
            setIsChatSending(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendChatMessage();
        }
    };

    return (
        <div className="p-4 bg-gray-200" style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            background: '#FFFFFF',
            border: '1px solid #BDC3C7',
            borderRadius: '8px'
        }}>
            {/* Chat Header */}
            <div style={{
                padding: '16px',
                borderBottom: '1px solid #BDC3C7',
                background: '#F8F9FA',
                borderRadius: '8px 8px 0 0'
            }}>
                <h3 style={{ 
                    margin: 0, 
                    color: '#2C3E50',
                    fontSize: '16px',
                    fontWeight: '600'
                }}>
                    Graph Chat Assistant
                </h3>
                <p style={{
                    margin: '4px 0 0 0',
                    fontSize: '12px',
                    color: '#7F8C8D'
                }}>
                    Ask questions about the graph or use commands like 'refresh', 'expand', or 'reset'
                </p>
            </div>

            {/* Chat Messages */}
            <div
                ref={chatMessagesRef}
                onScroll={handleChatScroll}
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '16px',
                    background: '#FFFFFF'
                }}
            >
                {chatMessages.length === 0 && (
                    <div style={{
                        textAlign: 'center',
                        color: '#95A5A6',
                        fontStyle: 'italic',
                        marginTop: '20px'
                    }}>
                        Start a conversation about the graph data...
                    </div>
                )}
                
                {chatMessages.map((message, index) => (
                    <div key={index} style={{
                        marginBottom: '12px',
                        padding: '12px',
                        borderRadius: '8px',
                        background: message.sender === 'You' ? '#E3F2FD' : 
                                   message.sender === 'AI' ? '#F3E5F5' : '#FFEBEE',
                        border: `1px solid ${message.sender === 'You' ? '#BBDEFB' : 
                                           message.sender === 'AI' ? '#E1BEE7' : '#FFCDD2'}`
                    }}>
                        <div style={{
                            fontWeight: 'bold',
                            fontSize: '12px',
                            color: message.sender === 'You' ? '#1976D2' : 
                                   message.sender === 'AI' ? '#7B1FA2' : '#D32F2F',
                            marginBottom: '4px'
                        }}>
                            {message.sender}
                        </div>
                        <div style={{
                            fontSize: '14px',
                            color: '#2C3E50',
                            lineHeight: '1.4',
                            whiteSpace: 'pre-wrap'
                        }}>
                            {message.text}
                        </div>
                    </div>
                ))}
                
                {isChatSending && (
                    <div style={{
                        padding: '12px',
                        textAlign: 'center',
                        color: '#7F8C8D',
                        fontStyle: 'italic'
                    }}>
                        <div style={{
                            display: 'inline-block',
                            animation: 'pulse 1.5s ease-in-out infinite'
                        }}>
                            Processing your request...
                        </div>
                    </div>
                )}
            </div>

            {/* Scroll to Bottom Button */}
            {showScrollToBottom && (
                <button
                    onClick={scrollToBottom}
                    style={{
                        position: 'absolute',
                        bottom: '80px',
                        right: '20px',
                        background: '#3498DB',
                        color: 'white',
                        border: 'none',
                        borderRadius: '20px',
                        padding: '8px 12px',
                        fontSize: '12px',
                        cursor: 'pointer',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                        zIndex: 10
                    }}
                >
                    ↓ Scroll to bottom
                </button>
            )}

            {/* Chat Input */}
            <div style={{
                padding: '16px',
                borderTop: '1px solid #BDC3C7',
                background: '#F8F9FA',
                borderRadius: '0 0 8px 8px'
            }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                        type="text"
                        value={chatInputValue}
                        onChange={(e) => setChatInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isChatSending || parentLoading}
                        placeholder={isChatSending ? "Sending..." : "Ask about the graph or type a command..."}
                        style={{
                            flex: 1,
                            padding: '12px',
                            border: '1px solid #BDC3C7',
                            borderRadius: '6px',
                            fontSize: '14px',
                            outline: 'none',
                            background: (isChatSending || parentLoading) ? '#F5F5F5' : '#FFFFFF'
                        }}
                    />
                    <button
                        onClick={handleSendChatMessage}
                        disabled={!chatInputValue.trim() || isChatSending || parentLoading}
                        style={{
                            padding: '12px 20px',
                            background: (!chatInputValue.trim() || isChatSending || parentLoading) ? '#95A5A6' : '#3498DB',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: (!chatInputValue.trim() || isChatSending || parentLoading) ? 'not-allowed' : 'pointer',
                            transition: 'background-color 0.2s'
                        }}
                    >
                        Send
                    </button>
                </div>
                <div style={{
                    fontSize: '11px',
                    color: '#7F8C8D',
                    marginTop: '8px'
                }}>
                    Press Enter to send • Try: "refresh", "expand", "show more data", or ask questions
                </div>
            </div>

            <style jsx>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `}</style>
        </div>
    );
};

export default ChatInterface;