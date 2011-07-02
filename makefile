ifeq ($(MAKECMDGOALS),analyze)
CXXFLAGS := $(shell llvm-config --cxxflags) -analyze
CXX := clang++
endif

EXE := uh
CXXFLAGS := $(shell llvm-config --cxxflags)
LLVMLDFLAGS := $(shell llvm-config --ldflags --libs)
SOURCES = src/uh.cpp \
    src/IncludeHandler.cpp
OBJECTS = $(SOURCES:.cpp=.o)
CLANGLIBS = -lclangRewrite \
    -lclangParse \
    -lclangSema \
    -lclangAnalysis \
    -lclangAST \
    -lclangDriver \
    -lclangSerialization \
	-lclangFrontend \
	-lclangLex \
	-lclangBasic \
	-lLLVMSupport \
	-lLLVMSystem \

$(EXE): $(OBJECTS) 
	$(CXX) $(OBJECTS) $(CLANGLIBS) $(LLVMLDFLAGS) -o src/$(EXE)

analyze: $(OBJECTS)
	$(CXX) $(OBJECTS) $(CLANGLIBS) $(LLVMLDFLAGS) -o src/$(EXE)

%: %.o
	$(CXX) -o $@ $< $(CLANGLIBS) $(LLVMLDFLAGS)

clean:
	-rm -f $(EXES) $(OBJECTS) *~
