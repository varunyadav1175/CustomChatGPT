"use client";
import React, { useState, createContext } from "react";
import ChatHistory from "@/component/ChatHistory";
import Chats from "@/component/Chats";

const chatdetail = createContext();
const emailDetail = createContext();

const Home = () => {
  const [chatlog, setChatlog] = useState([]);
  const [email, setEmail] = useState("");
  return (
    <div className="flex flex-row divide-x-2 divide-black dark:divide-gray-500">
      <chatdetail.Provider value={{ chatlog, setChatlog }}>
        <emailDetail.Provider value={{ email, setEmail }}>
          <ChatHistory />
          <Chats />
        </emailDetail.Provider>
      </chatdetail.Provider>
    </div>
  );
};

export default Home;
export { chatdetail, emailDetail };
