import React, { createContext, useState} from "react";

export const QubitContext = createContext();

export class Qubit {
    constructor(coordinates, index){
        this.location = coordinates;
        this.id = index;
        this.class = null;
        this.logical_observalble = false;
        this.label = "";
    }
    qubitFromCopy(qubit, newid){
        this.location = qubit.getLocation();
        this.id = newid;
        this.class = qubit.getClass();
        this.logical_observalble = qubit.getLogicalObservable();
        this.label = qubit.getLabel();
    }
    getid(){
        return(this.id);
    }
    getLocation(){
        return(this.location);
    }
    getLogicalObservable(){
        return(this.logical_observalble);
    }
    getClass(){
        return(this.class);
    }
    getLabel(){
        return(this.label);
    }
    setClass(classId){
        this.class = classId;
    }
    setLogicalObservable(){
        this.logical_observalble = !this.logical_observalble;
    }
    setLabel(label){
        this.label = label;
    }
}
export class QubitGroup {
    constructor(name, colour, index){
        this.name = name;
        this.colour = colour;
        this.index = index;
    }
}


export const QubitProvider = ({ children }) => {
    const [qubits, setQubits] = useState([]);
    const [qubitgroups, setQubitGroups] = useState([]);

    const addQubit = (coordinates, index) => {
        const newQubit = new Qubit(coordinates, index);
        setQubits((previousQubits) => [...previousQubits,newQubit]);
    }
    const removeQubit = (qubit) => {
        const qid = qubit.getid()
        setQubits(qubits.filter((q) => q.getid() !== qid));
    }
    const resetQubits = () => {
        setQubits([]);
    }
    const setLogicalObservablePerQubit = (qubit) =>{
        const qid = qubit.getid()
        setQubits((previousQubits) => {
            const updatedQubits = previousQubits.map((q) => 
                { 
                    if (q.getid() === qid){
                        const newQ = new Qubit(qubit.getLocation(), qid)
                        newQ.setLogicalObservable()
                        return newQ;
                    }
                    else{
                        return q;
                    }
                });
                return updatedQubits;
            })
     }
     const makeIdsConsecutive = () => {
        setQubits((previousQubits) => {
            const updatedQubits = previousQubits.map((q,newid) => 
                { 
                    
                        const newQ = new Qubit(q.getLocation(), newid);
                        newQ.qubitFromCopy(q,newid);
                        return newQ;
                    }
                );
                return updatedQubits;
            })

     }

    return(
        <QubitContext.Provider value={{qubits, addQubit, removeQubit, resetQubits, setLogicalObservablePerQubit,makeIdsConsecutive}}>
            {children}
        </QubitContext.Provider>
    );
}
