const noiseName = (index) => {
    switch (index) {
        case 0:
            return ("After single-qubit gate depolarization:");
        case 1:
            return ("After two-qubit gate depolarization:");
        case 2:
            return ("Before measurement flip probability:");
        case 3:
            return ("Before round data depolarization:");
        case 4:
            return ("After reset flip probability:")
        default:
            break;
    }
}

export default noiseName