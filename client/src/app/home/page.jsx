"use client";
import React, { useState, createContext } from "react";
import ChatHistory from "@/component/ChatHistory";
import Chats from "@/component/Chats";

const chatdetail = createContext();

const Home = () => {
  const [chatlog, setChatlog] = useState([]);
  return (
    <div className="flex flex-row divide-x-2 divide-black dark:divide-gray-500">
      <chatdetail.Provider value={{ chatlog, setChatlog }}>
        <ChatHistory />
        <Chats />
      </chatdetail.Provider>
    </div>
  );
};

export default Home;
export {chatdetail};
