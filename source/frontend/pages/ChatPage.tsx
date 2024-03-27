'use client'

import React, { useState } from "react";
import Sidebar from "@/components/Chat/Sidebar";
import ChatWindow from "@/components/Chat/ChatWindow";
import { ImageInfo } from "@/utils/types";
import SmallBar from "@/components/Chat/SmallBar";

const ChatPage: React.FC = () => {
    const [uploadedImages, setUploadedImages] = useState<ImageInfo[]>([]);
    const [keepTrack, setKeepTrack] = useState<boolean>(false);

    const handleImagesUploaded = (images: ImageInfo[]) => {
        setUploadedImages(images);
    };

    const handleKeepTrackChange = (keepTrack: boolean) => {
        console.log(keepTrack);
        setKeepTrack(keepTrack);
    }

    return (
        <div className="box-border overflow-y-hidden h-screen bg-white flex">
            <SmallBar />
            <Sidebar onImagesUploaded={handleImagesUploaded} onKeepTrackChange={handleKeepTrackChange} />
            <ChatWindow uploadedImages={uploadedImages} keepTrack={keepTrack} />
        </div>
    );
};

export default ChatPage;
