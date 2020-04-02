import React from 'react';
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
            items: result.items,
            donationsPDay: result.donations_per_day
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
            items: [[3093, "15.03.2020", "14:43:56", "tchurovtim@gmail.com", "Санкт-Петербург", "200"], [2, "15.03.2020", "14:43:56", "tchurovtim@gmail.com", "Санкт-Петербург", "200"]],
            // [["initial item"]]
            donationsPDay: {"15.03.2020": {"donations_that_day": 2,
                                           "sum_that_day": 400}
            }
        }
    }


    render() {
        console.log(this.state.items)
        return (
            <div>
                <table>
                {
                    this.state.items.map((item, i) => <DonationElem parentState={this.state} string={item} key={item.id} />)
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


    displaySpan(row){
        if(row === this.props.parentState.items.find((i) => i[1] === row[1])){
            let day_don= this.props.parentState.donationsPDay[row[1]]
            return <td rowSpan={day_don["donations_that_day"]}>{day_don["sum_that_day"]}</td>;
        }
    }


    render(){
        return(
            <React.Fragment>
                {<tr key={this.props.key}>{this.displayRow(this.props.string)}
                    {this.displaySpan(this.props.string)}
                </tr>}
            </React.Fragment>
        );
    }

}


export default App;
