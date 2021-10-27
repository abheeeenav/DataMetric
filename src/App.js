
import './App.css';
import React, { useEffect, useState } from "react";
import Nav from './components/navigation.js';
import { Header } from './components/Hero';
import { BrandLogo } from './components/BrandLogo';
import { Feature1 } from './components/feature1';
import { Feature2 } from './components/feature2';
import { CTA } from './components/cta';
import { foot, Footer, footerend } from './components/footerend';

function App() {
  return (
    <div className="App">
      <Nav />
      <Header />
      <BrandLogo />
      <Feature1 />
      <Feature2 />
      <CTA />
      <Footer />

    </div>
  );
}

export default App;
