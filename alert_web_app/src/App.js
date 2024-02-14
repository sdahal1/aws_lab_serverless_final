import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import React, { useState } from 'react';
import { usStates, languageOptions, countiesByState } from './data/state_county_data';
import NewSubscriberForm from './components/NewSubscriberForm';
import NavBar from './components/NavBar';
import { Routes, Route } from "react-router-dom";
import SendAlert from './components/SendAlert';

function App() {

  return (
    <div className='container'>
      <NavBar />
      <Routes>
        <Route path="/" element={<NewSubscriberForm />} />
        <Route path="/send-alert" element={<SendAlert/>} />
      </Routes>
    </div>

  );
}

export default App;