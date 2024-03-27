import React, { useState } from 'react';
import { ImageInfo, Message, SendMessageResponse } from "@/utils/types";
import MediaModal from './MediaModal';
import { MESSAGE_HOST } from '@/utils/api';

interface ChatWindowProps {
    uploadedImages: ImageInfo[];
    keepTrack: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ uploadedImages, keepTrack }) => {
    const [message, setMessage] = useState<string>("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [showWarning, setShowWarning] = useState<boolean>(false);
    const [showModal, setShowModal] = useState<boolean>(false);
    const [modalSrc, setModalSrc] = useState<string | null>(null);

    const resultData = uploadedImages.length > 0 ? uploadedImages.filter((img) => img.base64_string.startsWith('data:image')) : null;

    const sendMessage = async (): Promise<void> => {
        if (!message.trim()) {
            setShowWarning(true);
            return;
        }

        const tempMessageId = new Date().getTime();
        
        const tempMessage = {
            id: tempMessageId,
            text: message,
            media: [],
            isLoading: true,
        };

        setMessages(prevMessages => [...prevMessages, tempMessage]);

        setMessage('');

        setShowWarning(false);
        setIsLoading(true);

        const requestData = {
            instruction: message,
            images: resultData ?? 'None',
            keep_track: keepTrack,
        };

        try {
            const response = await fetch(`${MESSAGE_HOST}process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            if (!response.ok) throw new Error('Network response was not ok.');

            const data: SendMessageResponse = await response.json();

            let newMedia: string[] = [];
            if (data.result && Array.isArray(data.result)) {
                newMedia = data.result.map(base64 => `data:image/jpeg;base64,${base64}`);
            } else if (data.result && typeof data.result === 'string') {
                newMedia = [`data:video/mp4;base64,${data.result}`];
            }

            setMessages(prevMessages =>
                prevMessages.map(msg =>
                    msg.id === tempMessageId ? { ...msg, media: newMedia, isLoading: false } : msg
                )
            );
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setIsLoading(false);
            setMessage('');
        }
    };

    const openModal = (src: string): void => {
        setModalSrc(src);
        setShowModal(true);
    };

    const closeModal = (): void => {
        setShowModal(false);
        setModalSrc(null);
    };

    return (
        <div className="flex flex-col h-screen w-full px-4 py-2">
            <div className="flex-1 overflow-auto items-end flex-col-reverse flex gap-4">
                {messages.slice().reverse().map((msg, index) => (
                    <div key={index} className="flex flex-col items-end gap-4 w-full">
                        <div className="bg-background text-lg p-2 rounded-lg max-w-xs md:max-w-md lg:max-w-xl flex-grow self-end">
                            {msg.text}
                        </div>
                        {msg.media && msg.media.map((src, idx) => (
                            <div key={idx} className="flex-shrink-0 self-start cursor-pointer" onClick={() => openModal(src)}>
                                <img src={src} alt={`Result ${idx + 1}`} className="w-full h-72 object-cover rounded-lg" />
                            </div>
                        ))}
                    </div>
                ))}
                {showModal && <MediaModal isOpen={showModal} onClose={closeModal} src={modalSrc} />}
            </div>
            <div className="relative flex items-center pb-6 pt-2">
                {showWarning && (
                    <div className="text-red-500 absolute top-0 text-xs text-primary">
                        Warning: Please enter a message before sending.
                    </div>
                )}
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="flex-grow pl-4 pr-12 py-4 text-gray-700 bg-white border border-gray-300 rounded-full shadow-sm focus:outline-primary mt-4"
                    placeholder="Add your instruction here.."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <div className="relative inset-y-0 right-0 pr-2 flex items-center">
                    <button
                        onClick={sendMessage}
                        disabled={isLoading}
                        className={`p-2 focus:outline-none transition ease-in-out duration-300`}
                    >
                        {isLoading ? (
                            <svg className="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0116 0H4z"></path>
                            </svg>
                        ) : (
                            <svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={`stroke-primary hover:stroke-primary ${(isLoading) && 'cursor-not-allowed stroke-slate-300 hover:stroke-slate-300'}`}>
                                <path d="M11.5003 12H5.41872M5.24634 12.7972L4.24158 15.7986C3.69128 17.4424 3.41613 18.2643 3.61359 18.7704C3.78506 19.21 4.15335 19.5432 4.6078 19.6701C5.13111 19.8161 5.92151 19.4604 7.50231 18.7491L17.6367 14.1886C19.1797 13.4942 19.9512 13.1471 20.1896 12.6648C20.3968 12.2458 20.3968 11.7541 20.1896 11.3351C19.9512 10.8529 19.1797 10.5057 17.6367 9.81135L7.48483 5.24303C5.90879 4.53382 5.12078 4.17921 4.59799 4.32468C4.14397 4.45101 3.77572 4.78336 3.60365 5.22209C3.40551 5.72728 3.67772 6.54741 4.22215 8.18767L5.24829 11.2793C5.34179 11.561 5.38855 11.7019 5.407 11.8459C5.42338 11.9738 5.42321 12.1032 5.40651 12.231C5.38768 12.375 5.34057 12.5157 5.24634 12.7972Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatWindow;