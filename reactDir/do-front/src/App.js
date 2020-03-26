import React from 'react';
// import logo from './logo.svg';
import './App.css';

function App() {
    return (
        <div className="App">
            <header className="App-header">
            {/*<img src={logo} className="App-logo" alt="logo" />*/}
                <ListElem />
            </header>
        </div>
    );
}


class ListElem extends React.Component {
    componentDidMount() {
    fetch("/api/getList"
    )
        .then(res => res.json())
        .then(
        (result) => {
            this.setState({
            isLoaded: true,
            items: result.items
            });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
            this.setState({
                isLoaded: true,
                error
            });
        }
      )
    }

    constructor(props) {
        super(props);
        this.state = {
            items: // [[3093, "15.03.2020", "14:43:56", "tchurovtim@gmail.com", "Санкт-Петербург", "200"], [2, "15.03.2020", "14:43:56", "tchurovtim@gmail.com", "Санкт-Петербург", "200"]]
            [["initial item"]]
        }
    }


    render() {
        return (
            <div>
                <table>
                {
                    this.state.items.map((item, i) => <DonationElem string={item} key={item.id} />)
                }
                </table>
            </div>
        );
    }
}


class DonationElem extends React.Component {

    displayRow(row){
        return row.map((cell) => <td key={this.props.key + cell.toString()}>{cell}</td>)
    }

    render(){
        return(
            <React.Fragment>
                {<tr key={this.props.key}>{this.displayRow(this.props.string)}</tr>}
            </React.Fragment>
        );
    }

}


export default App;
