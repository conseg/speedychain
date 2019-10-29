package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"math/big"
	"net"
	"os"
	"strconv"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/rawdb"
	"github.com/ethereum/go-ethereum/core/state"
	"github.com/ethereum/go-ethereum/core/vm"
	"github.com/ethereum/go-ethereum/core/vm/runtime"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/params"
)

var rdb = rawdb.NewMemoryDatabase()
var estado *state.StateDB

//Struct para uma solicitação
type solicitacao struct {
	Tipo string //Tipo pode ser Exec, Criar ou Cham
	Data string
	From string
	To   string
	Root string // Root da patricia Merklee Tree
}

//Retorno Struct para retorno
type retorno struct {
	Ret  string // Valor retornado apos execução
	Root string // Root da patricia Merklee Tree
	Erro string
}

// Config is a basic type specifying certain configuration flags for running
// the EVM.

func main() {

	// Recebe solicitações pela porta 9090
	listener, err := net.Listen("tcp", ":6666")
	if err != nil {
		fmt.Printf("Rede: msg erro: %s\n", err)
		os.Exit(1)
	}

	estado, _ = state.New(common.HexToHash("56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"), state.NewDatabase(rdb))

	fmt.Println("Rede: Iniciando...")

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Printf("Rede: Erro durante conexão: %s \n", err)
			os.Exit(1)
		}

		fmt.Printf("Rede: Solicitação de: %s.\n ", conn.RemoteAddr())

		//Recebe a mensagem
		tbmsg := make([]byte, 6)
		bufio.NewReader(conn).Read(tbmsg)
		tmsg, err := strconv.Atoi(string(tbmsg))
		if err != nil {
			fmt.Printf("Rede: Erro recepção - %s \n", err)
		}

		fmt.Printf("Rede: Tamanho da msg %d\n", tmsg)
		bmsg := make([]byte, tmsg)
		//msg, _ := bufio.NewReader(conn).Read()

		trecebido, err := bufio.NewReader(conn).Read(bmsg)
		if err != nil {
			fmt.Printf("Rede: Erro recepção - %s \n", err)
		}
		fmt.Printf("Rede: Quantidade recebida da msg %d\n", trecebido)
		fmt.Printf("Solicitação: %s", bmsg)
		fmt.Printf("Transformação: Solicitação Recebida\n")
		var sol solicitacao
		json.Unmarshal(bmsg, &sol)
		fmt.Printf("Transformação: Solicitação transformada em JSON\n")

		// Seleciona o tipo de operação
		var (
			ret  string
			root string
		)

		if sol.Tipo == "Exec" {
			ret, err = Exec(sol.Data)
			root = common.Hash{}.Hex()

		} else if sol.Tipo == "Criar" {
			ret, root, err = Criar(sol.Data, sol.From, sol.Root)

		} else if sol.Tipo == "Cham" {
			ret, root, err = Cham(sol.Data, sol.From, sol.To, sol.Root)
		} else {
			fmt.Printf("Transformação: Comando não disponivel - %s.\n ", sol.Tipo)
		}

		//Remove o 0x do hex do root
		root = root[2:]

		//Devolve resultado
		var resp retorno
		if err == nil {
			resp = retorno{ret, root, ""}
		} else {
			resp = retorno{ret, root, err.Error()}
		}

		b, errt := json.Marshal(resp)
		if errt != nil {
			fmt.Printf("Envio: Erro durante resposta: %s \n", err)
		}

		fmt.Printf("Resultado: %s \n", string(b))

		fmt.Printf("tamanho da msg: %d\n", len(b))
		padded := fmt.Sprintf("%06d", len(b))

		conn.Write([]byte(padded)) // Envia tamanho
		conn.Write(b)

		bufio.NewReader(conn).ReadByte()
		fmt.Printf("Rede: Encerrando %s.\n ", conn.RemoteAddr())
	}
}

//Exec Executa um codigo de acordo com a EVM, mas não salva nada no banco de dados
func Exec(code2 string) (string, error) {

	code := common.Hex2Bytes(code2)
	fmt.Printf("Processo: Tipo Exec\n")
	cfg := new(runtime.Config)
	setDefaults(cfg)

	cfg.State, _ = state.New(common.Hash{}, state.NewDatabase(rawdb.NewMemoryDatabase()))

	var (
		address = common.BytesToAddress([]byte("contract"))
		vmenv   = runtime.NewEnv(cfg)
		sender  = vm.AccountRef(cfg.Origin)
	)

	cfg.State.SetCode(address, code)
	// set the receiver's (the executing contract) code for execution.
	cfg.State.SetCode(address, code)
	// Call the code with the given configuration.
	ret, _, err := vmenv.Call(
		sender,
		common.BytesToAddress([]byte("contract")),
		nil,
		cfg.GasLimit,
		cfg.Value,
	)
	fmt.Printf("Processo: Exec Completo\n")
	return common.Bytes2Hex(ret), err
}

//Criar Roda o comando create dentro da EVM e armazena o estado resultante
func Criar(input2, from2, root2 string) (add, rootRet string, err error) {
	input := common.Hex2Bytes(input2)
	from := common.Hex2Bytes(from2)
	root := common.Hex2Bytes(root2)
	fmt.Printf("Processo: Tipo Criar\n")
	cfg := new(runtime.Config)
	setDefaults(cfg)
	cfg.Origin = common.BytesToAddress(from)

	cfg.State = estado
	cfg.State.Reset(common.BytesToHash(root))
	var (
		vmenv    = runtime.NewEnv(cfg)
		sender   = vm.AccountRef(cfg.Origin)
		hashRoot common.Hash
	)

	cfg.State.CreateAccount(common.HexToAddress(from2))
	cfg.State.SetBalance(common.HexToAddress(from2), big.NewInt(100000))

	// Primeiro valor é o codigo retornado, mas não precisa devolver ele
	_, address, _, err := vmenv.Create(
		sender,
		input,
		cfg.GasLimit,
		cfg.Value,
	)

	hashRoot, _ = cfg.State.Commit(false) //manter

	return address.Hex(), hashRoot.Hex(), err
}

//Cham faz uma chamada para um contrato
func Cham(input2, from2, to2, root2 string) (ret2, rootRet string, err error) {
	input := common.Hex2Bytes(input2)
	to := common.Hex2Bytes(to2)
	from := common.Hex2Bytes(from2)
	root := common.Hex2Bytes(root2)
	fmt.Printf("Processo: Tipo Cham\n")
	cfg := new(runtime.Config)
	setDefaults(cfg)
	cfg.Origin = common.BytesToAddress(from)

	cfg.State = estado
	cfg.State.Reset(common.BytesToHash(root))

	fmt.Printf("CODIGO:: %s", common.Bytes2Hex(cfg.State.GetCode(common.BytesToAddress(to))))

	vmenv := runtime.NewEnv(cfg)
	sender := cfg.State.GetOrNewStateObject(cfg.Origin)

	var ret []byte
	ret, _, err = vmenv.Call(
		sender,
		common.BytesToAddress(to),
		input,
		cfg.GasLimit,
		cfg.Value,
	)

	hashRoot, _ := cfg.State.Commit(true)
	return common.Bytes2Hex(ret), hashRoot.Hex(), err
}

// sets defaults on the config
func setDefaults(cfg *runtime.Config) {
	if cfg.ChainConfig == nil {
		cfg.ChainConfig = &params.ChainConfig{
			ChainID:        big.NewInt(1),
			HomesteadBlock: new(big.Int),
			DAOForkBlock:   new(big.Int),
			DAOForkSupport: false,
			EIP150Block:    new(big.Int),
			EIP155Block:    new(big.Int),
			EIP158Block:    new(big.Int),
		}
	}

	if cfg.Difficulty == nil {
		cfg.Difficulty = new(big.Int)
	}
	if cfg.Time == nil {
		cfg.Time = big.NewInt(time.Now().Unix())
	}
	if cfg.GasLimit == 0 {
		cfg.GasLimit = math.MaxUint64
	}
	if cfg.GasPrice == nil {
		cfg.GasPrice = new(big.Int)
	}
	if cfg.Value == nil {
		cfg.Value = new(big.Int)
	}
	if cfg.BlockNumber == nil {
		cfg.BlockNumber = new(big.Int)
	}
	if cfg.GetHashFn == nil {
		cfg.GetHashFn = func(n uint64) common.Hash {
			return common.BytesToHash(crypto.Keccak256([]byte(new(big.Int).SetUint64(n).String())))
		}
	}
}