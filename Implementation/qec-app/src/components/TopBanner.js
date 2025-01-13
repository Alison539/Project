import React from "react";
import "./styles.css";

const TopBanner = ({title, description}) => {
  return (
    <div className = "banner">
        <h1 className = "banner-title"> {title} </h1>
        <p className = "banner-subtext"> {description} </p>
    </div>
  );
};

export default TopBanner; 
