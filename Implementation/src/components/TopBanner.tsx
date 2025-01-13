import React from "react";
import "./styles.css";

interface TopBannerProps {
  title: string;
  description: string;
}

const TopBanner = ({title, description}: TopBannerProps) => {
  return (
    <div className = "banner">
        <h1 className = "banner-title"> {title} </h1>
        <p className = "banner-subtext"> {description} </p>
    </div>
  );
};

export default TopBanner; 
