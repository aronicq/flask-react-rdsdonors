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
            items: ["initial element"]
        }
    }


    render() {
        return (
            <div>
                {
                    this.state.items.map((item, i) => <DonationElem string={item} key={item.id} />)
                }
            </div>
        );
    }
}


class DonationElem extends React.Component {

    // display(list){
    //     return(
    //         list.map(t => t).reduce((prev, curr) => [prev, ', ', curr])
    //     )
    // }

    render(){
        return(
            <div>
                {this.props.string}
            </div>
        );
    }

}


export default App;
